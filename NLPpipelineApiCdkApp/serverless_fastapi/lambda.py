import os
from apig_wsgi import make_lambda_handler
from serverless_fastapi import create_app


def configure_logger():
    from logging.config import dictConfig

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",  # noqa
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {
                "level": os.environ.get("ROOT_LOG_LEVEL", "INFO"),
                "handlers": ["wsgi"],
            },
        }
    )


configure_logger()
app = create_app()

inner_handler = make_lambda_handler(app, binary_support=True)


def lambda_handler(event, context):
    try:
        app.logger.debug(event)
        headers = event["headers"]
        # we passed host from CloudFront function in the field
        #  X-Forwarded-Host
        cf_host = headers.pop("X-Forwarded-Host", None)
        if cf_host:
            app.config["SERVER_NAME"] = cf_host
            # patch host header
            headers["Host"] = cf_host
            event["multiValueHeaders"]["Host"] = [cf_host]
            app.logger.info(
                f"Host header is successfully patched to {cf_host}"
            )

        return inner_handler(event, context)
    except:  # noqa
        app.logger.exception("Exception handling lambda")
        raise
