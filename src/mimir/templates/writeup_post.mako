<%inherit file="layout.mako"/>
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="${request.route_path('index')}">Home</a></li>
    <li class="breadcrumb-item"><a href="${request.route_path('writeup', writeup_id=writeup.id)}">Writeup: ${writeup.id} - ${writeup.title} - ${writeup.author}</a></li>
    <li class="breadcrumb-item active" aria-current="page">Post: ${post.index} - ${post.title}</li>
  </ol>
</nav>

<form action="${request.route_path('writeup_post', writeup_id=writeup.id, post_index=post.index)}" method="POST">
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="post-title">Title:</label>
    <div class="col-sm-10">
        <input type="text" class="form-control" id="post-title" value="${post.title}" name="title">
    </div>
  </div>
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="post-author">Author:</label>
    <div class="col-sm-10">
        <input type="text" class="form-control" id="post-author" value="${post.author}" name="author">
    </div>
  </div>
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="post-ordinal">Ordinal:</label>
    <div class="col-sm-10">
        <input type="text" class="form-control" id="post-ordinal" value="${post.ordinal}" name="ordinal">
    </div>
  </div>
  <div class="form-group row">
    <div class="offset-sm-2 col-sm-10">
      <div class="custom-control custom-switch">
        <input type="checkbox" class="custom-control-input" id="post-published" value="true" name="published"${" checked" if post.published else ""}>
        <label class="custom-control-label" for="post-published">Published</label>
      </div>
    </div>
  </div>

  <div class="form-group row">
    <button type="submit" class="btn btn-success col-sm-2">Save</button>
    <button type="reset" class="btn btn-danger col-sm-2 offset-sm-8">Reset</button>
  </div>
</form>

<table class="table table-striped table-hover">
    <thead>
        <tr>
            <th>Version</th>
            <th>Active</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
% for version in post.versions:
      <tr>
          <td>${version.version}</td>
          <td>${version.active}</td>
          <td>
          <form class="form-inline" method="POST" action="${request.route_path('writeup_post_version_activate', writeup_id=writeup.id, post_index=post.index, version=version.version)}">
          <a href="${request.route_path('writeup_post_version_preview', writeup_id=writeup.id, post_index=post.index, version=version.version)}" class="btn btn-info mr-2">Preview</a>
          <a href="${request.route_path('writeup_post_version_edit', writeup_id=writeup.id, post_index=post.index, version=version.version)}" class="btn btn-warning mr-2">Edit</a>
          % if not version.active:
          <button type="submit" class="btn btn-success mr-2">Activate</button>
          % endif
          </form>
          </td>
      </tr>
% endfor
    </tbody>
</table>