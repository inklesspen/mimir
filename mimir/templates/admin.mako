<%! import json %>
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="page_description">

        <title>Fnord</title>

        <link href="${request.static_path('mimir:static/css/bootstrap-custom.min.css')}" rel="stylesheet">
        <link href="${request.static_path('mimir:static/css/font-awesome-4.0.3.css')}" rel="stylesheet">
        <link href="${request.static_path('mimir:static/css/base.css')}" rel="stylesheet">
% if iframeDevtools:
        <script>
         __REACT_DEVTOOLS_GLOBAL_HOOK__ = parent.__REACT_DEVTOOLS_GLOBAL_HOOK__;
         window.connectIframeAltDevtools = true;
        </script>
% else:
        <script>
         window.connectIframeAltDevtools = false;
        </script>
% endif
    </head>

    <body>
      <div id="ReactApp"></div>
      <script type="text/javascript">
        var mimirData = ${bootstrap | n, json.dumps};
      </script>
      <script src="https://login.persona.org/include.js"></script>
      <script src="${request.static_path('mimir:static/mimir.js')}"></script>
    </body>
</html>
