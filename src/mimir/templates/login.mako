<%inherit file="layout.mako"/>
<form action="${request.route_path('login')}" method="POST">
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="username">Username:</label>
    <div class="col-sm-10">
        <input type="text" class="form-control" id="username" name="username">
    </div>
  </div>
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="password">Password:</label>
    <div class="col-sm-10">
        <input type="password" class="form-control" id="password" name="password">
    </div>
  </div>

  <div class="form-group row">
    <button type="submit" class="btn btn-success col-sm-2">Submit</button>
    <button type="reset" class="btn btn-danger col-sm-2 offset-sm-8">Reset</button>
  </div>
</form>