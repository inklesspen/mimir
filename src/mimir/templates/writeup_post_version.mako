<%inherit file="layout.mako"/>
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="${request.route_path('index')}">Home</a></li>
    <li class="breadcrumb-item"><a href="${request.route_path('writeup', writeup_id=writeup.id)}">Writeup: ${writeup.id} - ${writeup.title} - ${writeup.author}</a></li>
    <li class="breadcrumb-item"><a href="${request.route_path('writeup_post', writeup_id=post.writeup_id, post_index=post.index)}">Post: ${post.index} - ${post.title}</a></li>
    <li class="breadcrumb-item active" aria-current="page">Version: ${wpv.version}</li>
  </ol>
</nav>
% if mode == "preview":
${wpv.html_with_fixed_image_urls(request) | n}
% else:
<form action="${request.route_path('writeup_post_version_edit', **request.matchdict)}" method="POST">
  <div class="form-group">
    <div class="col-sm-12">
        <textarea class="form-control" name="html" rows="20">${wpv.html | n}</textarea>
    </div>
  </div>

  <div class="form-group row">
    <button type="submit" class="btn btn-success col-sm-2">Save</button>
    <button type="reset" class="btn btn-danger col-sm-2 offset-sm-8">Reset</button>
  </div>
</form>
% endif