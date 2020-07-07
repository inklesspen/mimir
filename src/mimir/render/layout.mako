<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400;1,600;1,700&display=swap" rel="stylesheet">
    <title><%block name="title">FATAL & Friends</%block></title>
    <link href="${request.route_path('rendered_static_file', filename='styles.css')}" rel="stylesheet">
<%block name="in_header"/>
</head>
  <body>
<main>
${ next.body() }
</main>
## <script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.15/lodash.min.js" integrity="sha512-3oappXMVVac3Ge3OndW0WqpGTWx9jjRJA8SXin8RxmPfc8rg87b31FGy14WHG/ZMRISo9pBjezW9y00RYAEONA==" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cash/8.0.0/cash.min.js" integrity="sha512-EDhfzQEETF4We0xjf0WaLReOGNgsUrXpApjCbIb7ruY4DL5wU6iFPyXPXptxdwQShwBvq8iMUQN4C93UVSXD+w==" crossorigin="anonymous"></script>
<%block name="in_footer"/>
  </body>
</html>

