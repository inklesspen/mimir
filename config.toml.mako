[application.development]
use = "egg:mimir#main"

"pyramid.reload_templates" = "true"
"pyramid.debug_authorization" = "false"
"pyramid.debug_notfound" = "false"
"pyramid.debug_routematch" = "false"
"pyramid.default_locale_name" = "en"
"pyramid.includes" = ["pyramid_debugtoolbar", "pyramid_tm"]

"sqlalchemy.url" = "postgresql://postgres@${environ['POSTGRES_PORT_5432_TCP_ADDR']}:${environ['POSTGRES_PORT_5432_TCP_PORT']}/postgres"

"debugtoolbar.hosts" = ["0.0.0.0/0"]
# "debugtoolbar.hosts" = ["127.0.0.1", "::1"]

"mimir.react_iframe_devtools" = true

[application.development.hashfs]
location = "/data/hashfs"

[application.production]
use = "egg:mimir#main"

"pyramid.reload_templates" = "false"
"pyramid.debug_authorization" = "false"
"pyramid.debug_notfound" = "false"
"pyramid.debug_routematch" = "false"
"pyramid.default_locale_name" = "en"
"pyramid.includes" = ["pyramid_tm"]

"mimir.react_iframe_devtools" = false

"sqlalchemy.url" = "postgresql://postgres@${environ['POSTGRES_PORT_5432_TCP_ADDR']}:${environ['POSTGRES_PORT_5432_TCP_PORT']}/postgres"

[server.development]
port = "6543"
host = "0.0.0.0"
use = "egg:waitress#main"

[server.production]
port = "8080"
host = "0.0.0.0"
use = "egg:waitress#main"

[logging.development]
version = 1

[logging.development.handlers]

[logging.development.handlers.console]
level = "NOTSET"
stream = "ext://sys.stderr"
formatter = "generic"
class = "logging.StreamHandler"

[logging.development.loggers]

[logging.development.loggers."sqlalchemy.engine"]
# "level = INFO" logs SQL queries.
# "level = DEBUG" logs SQL queries and results.
# "level = WARN" logs neither.  (Recommended for production systems.)
level = "INFO"
handlers = []

[logging.development.loggers.mimir]
level = "DEBUG"
handlers = []

[logging.development.root]
level = "INFO"
handlers = ["console"]

[logging.development.formatters]

[logging.development.formatters.generic]
format = "%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s"

[logging.production]
version = 1

[logging.production.handlers]

[logging.production.handlers.console]
level = "NOTSET"
stream = "ext://sys.stderr"
formatter = "generic"
class = "logging.StreamHandler"

[logging.production.loggers]

[logging.production.loggers."sqlalchemy.engine"]
# "level = INFO" logs SQL queries.
# "level = DEBUG" logs SQL queries and results.
# "level = WARN" logs neither.  (Recommended for production systems.)
level = "WARN"
handlers = []

[logging.production.loggers.mimir]
level = "WARN"
handlers = []

[logging.production.root]
level = "WARN"
handlers = ["console"]

[logging.production.formatters]

[logging.production.formatters.generic]
format = "%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s"
