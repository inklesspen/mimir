<!DOCTYPE html>
<html>
<head>
    <title><%block name="title">FATAL & Friends</%block></title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <link rel="stylesheet" href="${request.static_url('mimir:static/bootstrap.css')}">
    <link rel="stylesheet" href="${request.static_url('mimir:static/site.css')}">
% if 'ga.tracking_id' in request.registry.settings:
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', '${request.registry.settings['ga.tracking_id']}', 'auto');
  ga('send', 'pageview');
</script>
% endif
</head>
<body>
    <div class="container">
${self.body()}
    </div>
    <script src="${request.static_path('mimir:static/public.js')}"></script>
</body>
</html>
