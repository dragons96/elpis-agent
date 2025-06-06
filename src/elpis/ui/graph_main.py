import json
import logging
import os
import pathlib
import urllib.error
import threading
import typing
from typing import Optional, Mapping, Sequence

import click
from langgraph_api.cli import AuthConfig, patch_environment, _get_ls_origin, _get_org_id

if typing.TYPE_CHECKING:
    from langgraph_api.config import StoreConfig, HttpConfig


@click.option(
    "--host",
    default="127.0.0.1",
    help="Network interface to bind the development server to. Default 127.0.0.1 is recommended for security. Only use 0.0.0.0 in trusted networks",
)
@click.option(
    "--port",
    default=2024,
    type=int,
    help="Port number to bind the development server to. Example: langgraph dev --port 8000",
)
@click.option(
    "--no-reload",
    is_flag=True,
    default=True,
    help="Disable automatic reloading when code changes are detected",
)
@click.option(
    "--n-jobs-per-worker",
    default=None,
    type=int,
    help="Maximum number of concurrent jobs each worker process can handle. Default: 10",
)
@click.option(
    "--no-browser",
    is_flag=True,
    help="Skip automatically opening the browser when the server starts",
)
@click.option(
    "--debug-port",
    default=None,
    type=int,
    help="Enable remote debugging by listening on specified port. Requires debugpy to be installed",
)
@click.option(
    "--wait-for-client",
    is_flag=True,
    help="Wait for a debugger client to connect to the debug port before starting the server",
    default=False,
)
@click.option(
    "--studio-url",
    type=str,
    default=None,
    help="URL of the LangGraph Studio instance to connect to. Defaults to https://smith.langchain.com",
)
@click.option(
    "--allow-blocking",
    is_flag=True,
    help="Don't raise errors for synchronous I/O blocking operations in your code.",
    default=True,
)
@click.option(
    "--tunnel",
    is_flag=True,
    help="Expose the local server via a public tunnel (in this case, Cloudflare) "
    "for remote frontend access. This avoids issues with browsers "
    "or networks blocking localhost connections.",
    default=False,
)
@click.option(
    "--server-log-level",
    type=str,
    default="WARNING",
    help="Set the log level for the API server.",
)
@click.option('--env_file', default=None, help='Path to a .env file')
@click.option('--lang', default='en', type=click.Choice(['en', 'zh']),
              help='Language to use for the tool. Default is "en"')
@click.command(
    help="🏃‍♀️‍➡️ Run LangGraph API server in development mode with hot reloading and debugging support",
)
def dev(
    host: str,
    port: int,
    no_reload: bool,
    n_jobs_per_worker: Optional[int],
    no_browser: bool,
    debug_port: Optional[int],
    wait_for_client: bool,
    studio_url: Optional[str],
    allow_blocking: bool,
    tunnel: bool,
    server_log_level: str,
    env_file: str,
    lang: str,
):
    """CLI entrypoint for running the LangGraph API server."""

    if env_file:
        os.environ['ELPIS_ENV_FILE'] = env_file

    os.environ['LANG'] = lang

    langgraph_json_path = os.path.join(os.path.dirname(__file__), 'langgraph.json')

    import langgraph_cli.config


    config_json = langgraph_cli.config.validate_config_file(pathlib.Path(langgraph_json_path))
    if config_json.get("node_version"):
        raise click.UsageError(
            "In-mem server for JS graphs is not supported in this version of the LangGraph CLI. Please use `npx @langchain/langgraph-cli` instead."
        ) from None

    graphs = {
        'agent': f'elpis.ui.graph:graph'
    }

    run_server(
        host,
        port,
        not no_reload,
        graphs,
        n_jobs_per_worker=n_jobs_per_worker,
        open_browser=not no_browser,
        debug_port=debug_port,
        env=env_file,
        store=config_json.get("store"),
        wait_for_client=wait_for_client,
        auth=config_json.get("auth"),
        http=config_json.get("http"),
        ui=config_json.get("ui"),
        ui_config=config_json.get("ui_config"),
        studio_url=studio_url,
        allow_blocking=allow_blocking,
        tunnel=tunnel,
        server_level=server_log_level,
    )


def run_server(
    host: str = "127.0.0.1",
    port: int = 2024,
    reload: bool = False,
    graphs: dict | None = None,
    n_jobs_per_worker: int | None = None,
    env_file: str | None = None,
    open_browser: bool = False,
    tunnel: bool = False,
    debug_port: int | None = None,
    wait_for_client: bool = False,
    env: str | pathlib.Path | Mapping[str, str] | None = None,
    reload_includes: Sequence[str] | None = None,
    reload_excludes: Sequence[str] | None = None,
    store: typing.Optional["StoreConfig"] = None,
    auth: AuthConfig | None = None,
    http: typing.Optional["HttpConfig"] = None,
    ui: dict | None = None,
    ui_config: dict | None = None,
    studio_url: str | None = None,
    disable_persistence: bool = False,
    allow_blocking: bool = False,
    runtime_edition: typing.Literal["inmem", "community", "postgres"] = "inmem",
    server_level: str = "WARNING",
    **kwargs: typing.Any,
):
    """Run the LangGraph API server."""

    from langgraph_api.cli import logger

    import inspect
    import time

    import uvicorn

    start_time = time.time()

    env_vars = env if isinstance(env, Mapping) else None
    mount_prefix = None
    if http is not None and http.get("mount_prefix") is not None:
        mount_prefix = http.get("mount_prefix")
    if os.environ.get("LANGGRAPH_MOUNT_PREFIX"):
        mount_prefix = os.environ.get("LANGGRAPH_MOUNT_PREFIX")
    if isinstance(env, str | pathlib.Path):
        from dotenv.main import DotEnv

        env_vars = DotEnv(dotenv_path=env, encoding='utf-8').dict() or {}
        logger.debug(f"Loaded environment variables from {env}: {sorted(env_vars)}")


    if debug_port is not None:
        try:
            import debugpy
        except ImportError:
            logger.warning("debugpy is not installed. Debugging will not be available.")
            logger.info("To enable debugging, install debugpy: pip install debugpy")
            return
        debugpy.listen((host, debug_port))
        logger.info(
            f"🐛 Debugger listening on port {debug_port}. Waiting for client to attach..."
        )
        logger.info("To attach the debugger:")
        logger.info("1. Open your python debugger client (e.g., Visual Studio Code).")
        logger.info(
            "2. Use the 'Remote Attach' configuration with the following settings:"
        )
        logger.info("   - Host: 0.0.0.0")
        logger.info(f"   - Port: {debug_port}")
        logger.info("3. Start the debugger to connect to the server.")
        if wait_for_client:
            debugpy.wait_for_client()
            logger.info("Debugger attached. Starting server...")

    # Determine local or tunneled URL
    upstream_url = f"http://{host}:{port}"
    if mount_prefix:
        upstream_url += mount_prefix
    if tunnel:
        logger.info("Starting Cloudflare Tunnel...")
        from concurrent.futures import TimeoutError as FutureTimeoutError

        from langgraph_api.tunneling.cloudflare import start_tunnel

        tunnel_obj = start_tunnel(port)
        try:
            public_url = tunnel_obj.url.result(timeout=30)
        except FutureTimeoutError:
            logger.warning(
                "Timed out waiting for Cloudflare Tunnel URL; using local URL %s",
                upstream_url,
            )
            public_url = upstream_url
        except Exception as e:
            tunnel_obj.process.kill()
            raise RuntimeError("Failed to start Cloudflare Tunnel") from e
        local_url = public_url
        if mount_prefix:
            local_url += mount_prefix
    else:
        local_url = upstream_url
    to_patch = dict(
        MIGRATIONS_PATH="__inmem",
        DATABASE_URI=":memory:",
        REDIS_URI="fake",
        N_JOBS_PER_WORKER=str(n_jobs_per_worker if n_jobs_per_worker else 1),
        LANGGRAPH_STORE=json.dumps(store) if store else None,
        LANGSERVE_GRAPHS=json.dumps(graphs) if graphs else None,
        LANGSMITH_LANGGRAPH_API_VARIANT="local_dev",
        LANGGRAPH_AUTH=json.dumps(auth) if auth else None,
        LANGGRAPH_HTTP=json.dumps(http) if http else None,
        LANGGRAPH_UI=json.dumps(ui) if ui else None,
        LANGGRAPH_UI_CONFIG=json.dumps(ui_config) if ui_config else None,
        LANGGRAPH_UI_BUNDLER="true",
        LANGGRAPH_API_URL=local_url,
        LANGGRAPH_DISABLE_FILE_PERSISTENCE=str(disable_persistence).lower(),
        LANGGRAPH_RUNTIME_EDITION=runtime_edition,
        # If true, we will not raise on blocking IO calls (via blockbuster)
        LANGGRAPH_ALLOW_BLOCKING=str(allow_blocking).lower(),
        # See https://developer.chrome.com/blog/private-network-access-update-2024-03
        ALLOW_PRIVATE_NETWORK="true",
    )
    if env_vars is not None:
        # Don't overwrite.
        for k, v in env_vars.items():
            if k in to_patch:
                logger.debug(f"Skipping loaded env var {k}={v}")
                continue
            to_patch[k] = v
    with patch_environment(
        **to_patch,
    ):
        studio_origin = studio_url or _get_ls_origin() or "https://smith.langchain.com"
        full_studio_url = f"{studio_origin}/studio/?baseUrl={local_url}"

        def _open_browser():
            nonlocal studio_origin, full_studio_url
            import time
            import urllib.request
            import webbrowser
            from concurrent.futures import ThreadPoolExecutor

            thread_logger = logging.getLogger("browser_opener")
            if not thread_logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter("%(message)s"))
                thread_logger.addHandler(handler)

            with ThreadPoolExecutor(max_workers=1) as executor:
                org_id_future = executor.submit(_get_org_id)

                while True:
                    try:
                        with urllib.request.urlopen(f"{local_url}/ok") as response:
                            if response.status == 200:
                                try:
                                    org_id = org_id_future.result(timeout=3.0)
                                    if org_id:
                                        full_studio_url = f"{studio_origin}/studio/?baseUrl={local_url}&organizationId={org_id}"
                                except TimeoutError as e:
                                    thread_logger.debug(
                                        f"Failed to get organization ID: {str(e)}"
                                    )
                                    pass
                                thread_logger.info(
                                    f"Server started in {time.time() - start_time:.2f}s"
                                )
                                thread_logger.info(
                                    "🎨 Opening Studio in your browser..."
                                )
                                thread_logger.info("URL: " + full_studio_url)
                                webbrowser.open(full_studio_url)
                                return
                    except urllib.error.URLError:
                        pass
                    time.sleep(0.1)

        welcome = f"""

        Welcome to

╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

- 🚀 API: \033[36m{local_url}\033[0m
- 🎨 Studio UI: \033[36m{full_studio_url}\033[0m
- 📚 API Docs: \033[36m{local_url}/docs\033[0m

This in-memory server is designed for development and testing.
For production use, please use LangGraph Cloud.

"""
        logger.info(welcome)
        if open_browser:
            threading.Thread(target=_open_browser, daemon=True).start()
        supported_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k in inspect.signature(uvicorn.run).parameters
        }
        server_level = server_level.upper()
        uvicorn.run(
            "langgraph_api.server:app",
            host=host,
            port=port,
            reload=reload,
            env_file=env_file,
            access_log=False,
            reload_includes=reload_includes,
            reload_excludes=reload_excludes,
            log_config={
                "version": 1,
                "incremental": False,
                "disable_existing_loggers": False,
                "formatters": {
                    "simple": {
                        "class": "langgraph_api.logging.Formatter",
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "simple",
                        "stream": "ext://sys.stdout",
                    }
                },
                "loggers": {
                    "uvicorn": {"level": server_level},
                    "uvicorn.error": {"level": server_level},
                    "langgraph_api.server": {"level": server_level},
                },
                "root": {"handlers": ["console"]},
            },
            **supported_kwargs,
        )
