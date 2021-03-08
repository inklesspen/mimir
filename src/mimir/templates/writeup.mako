<%inherit file="layout.mako"/>
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="${request.route_path('index')}">Home</a></li>
    <li class="breadcrumb-item active" aria-current="page">Writeup: ${writeup.id} - ${writeup.title} - ${writeup.author}</li>
  </ol>
</nav>

<form action="${request.route_path('writeup', writeup_id=writeup.id)}" method="POST">
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="writeup-title">Title:</label>
    <div class="col-sm-10">
        <input type="text" class="form-control" id="writeup-title" value="${writeup.title}" name="title">
    </div>
  </div>
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="writeup-author">Author:</label>
    <div class="col-sm-10">
        <input type="text" class="form-control" id="writeup-author" value="${writeup.author}" name="author">
    </div>
  </div>
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="writeup-writeup-slug">Writeup Slug:</label>
    <div class="col-sm-8">
        <input type="text" readonly class="form-control-plaintext" id="writeup-writeup-slug" value="${writeup.writeup_slug}" name="writeup_slug">
    </div>
    <button type="button" class="btn btn-danger col-sm-2 break-glass" data-target="#writeup-writeup-slug">Break Glass</button>
  </div>
  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="writeup-author-slug">Author Slug:</label>
    <div class="col-sm-8">
        <input type="text" readonly class="form-control-plaintext" id="writeup-author-slug" value="${writeup.author_slug}" name="author_slug">
    </div>
    <button type="button" class="btn btn-danger col-sm-2 break-glass" data-target="#writeup-author-slug">Break Glass</button>
  </div>

  <div class="form-group row">
    <label class="col-sm-2 col-form-label" for="writeup-status">Status:</label>
    <div class="col-sm-10">
      <select class="custom-select" id="writeup-status" name="status">
        <option disabled>Select…</option>
        <option value="ongoing"${" selected" if writeup.status == "ongoing" else ""}>Ongoing</option>
        <option value="abandoned"${" selected" if writeup.status == "abandoned" else ""}>Abandoned</option>
        <option value="completed"${" selected" if writeup.status == "completed" else ""}>Completed</option>
      </select>
    </div>
  </div>

  <div class="form-group row">
    <div class="offset-sm-2 col-sm-10">
      <div class="custom-control custom-switch">
        <input type="checkbox" class="custom-control-input" id="writeup-published" value="true" name="published"${" checked" if writeup.published else ""}>
        <label class="custom-control-label" for="writeup-published">Published</label>
      </div>
    </div>
  </div>
  <div class="form-group row">
    <div class="offset-sm-2 col-sm-10">
      <div class="custom-control custom-switch">
        <input type="checkbox" class="custom-control-input" id="writeup-offensive" value="true" name="offensive_content"${" checked" if writeup.offensive_content else ""}>
        <label class="custom-control-label" for="writeup-offensive">Offensive Content</label>
      </div>
    </div>
  </div>
  <div class="form-group row">
    <div class="offset-sm-2 col-sm-10">
      <div class="custom-control custom-switch">
        <input type="checkbox" class="custom-control-input" id="writeup-triggery" value="true" name="triggery_content"${" checked" if writeup.triggery_content else ""}>
        <label class="custom-control-label" for="writeup-triggery">Triggery Content</label>
      </div>
    </div>
  </div>

  <div class="form-group row">
    <button type="submit" class="btn btn-success col-sm-2">Save</button>
    <button type="reset" class="btn btn-danger col-sm-2 offset-sm-8">Reset</button>
  </div>
</form>
<%block name="in_footer">
<script>
$(() => {
  $('.break-glass').on('click', (evt) => {
    const btn = $(evt.target);
    const target = btn.data('target');
    const targetEl = $(target);
    targetEl.prop('readonly', false);
    targetEl.removeClass('form-control-plaintext');
    targetEl.addClass('form-control');
    const div = targetEl.parent();
    div.removeClass('col-sm-8');
    div.addClass('col-sm-10');
    btn.remove();
  })
});
</script>
</%block>

<table class="table table-striped table-hover">
    <thead>
        <tr>
            <th>Title</th>
            <th>Author</th>
            <th>Ordinal</th>
        </tr>
    </thead>
    <tbody>
% for post in writeup.posts:
      <tr>
          <td><a href="${request.route_path('writeup_post', writeup_id=writeup.id, post_index=post.index)}">${post.title}</a></td>
          <td>${post.author}</td>
          <td>${post.ordinal}</td>
      </tr>
% endfor
    </tbody>
</table>