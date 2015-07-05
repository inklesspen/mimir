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
<p>
These writeups are extracted from the SA Forum's "FATAL & Friends" thread. Some of them are obscure RPGs. Some of them are very bad RPGs.
</p>
${self.body()}
    </div>
</body>
</html>
