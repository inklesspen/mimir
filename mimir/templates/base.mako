<!DOCTYPE html>
<html>
<head>
    <title><%block name="title">FATAL & Friends</%block></title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <link rel="stylesheet" href="${request.static_url('mimir:static/bootstrap.css')}">
    <link rel="stylesheet" href="${request.static_url('mimir:static/site.css')}">
</head>
<body>
    <div class="container">
${self.body()}
    </div>
    <script src="${request.static_path('mimir:static/public.js')}"></script>
</body>
</html>
