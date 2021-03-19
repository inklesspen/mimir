<%inherit file="layout.mako"/>
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="${request.route_path('index')}">Home</a></li>
    <li class="breadcrumb-item active" aria-current="page">${wpv.thread_post.id} - ${wpv.thread_post.author}</li>
  </ol>
</nav>

<div class="card">
    <div class="card-header">

    <form action="${request.route_path('extracted_post', post_id=wpv.id)}" method="POST">
        <div class="form-group row" id="writeup-row">
            <label class="col-sm-2 col-form-label" for="writeup">Writeup:</label>
            <div class="col-sm-10">
            <select class="custom-select" id="writeup" name="writeup_id">
                <option value="--" disabled="disabled">-- Choose --</option>
                <option value="w">New Writeup</option>
                <option value="--2" disabled="disabled">--</option>
% for writeup in likely_writeups:
                <option value="${writeup.id}"${" selected" if loop.first else ""}>${writeup.title} - ${writeup.author}</option>
% if loop.last:
                <option value="--2" disabled="disabled">--</option>
% endif
% endfor
% for writeup in other_writeups:
                <option value="${writeup.id}">${writeup.title} - ${writeup.author}</option>
% endfor
            </select>
            </div>
        </div>
<%def name="writeup_post_options(writeup=None)">
                <option value="--" disabled="disabled">-- Choose --</option>
                <option value="wp">New Post</option>
% if writeup is None:
<% return STOP_RENDERING %>
% endif
                <option value="--2" disabled="disabled">--</option>
% for wp in writeup.posts:
                <option value=${wp.id}>${wp.ordinal} - ${wp.title} - ${wp.author}</option>
% endfor
</%def>
        <div class="form-group row" id="writeup-post-row">
            <label class="col-sm-2 col-form-label" for="writeup-post">Post:</label>
            <div class="col-sm-10">
                <select class="custom-select" id="writeup-post" name="writeup_post_id">
                ${writeup_post_options(likely_writeups[0] if has_likely_writeup else None)}
                </select>
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-2 col-form-label" for="writeup-title">Writeup Title:</label>
            <div class="col-sm-10">
                <input type="text" class="form-control" id="writeup-title" value="" name="writeup_title">
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-2 col-form-label" for="writeup-author">Writeup Author:</label>
            <div class="col-sm-10">
                <input type="text" class="form-control" id="writeup-author" value="" name="writeup_author">
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-2 col-form-label" for="post-title">Post Title:</label>
            <div class="col-sm-10">
                <input type="text" class="form-control" id="post-title" value="" name="post_title">
            </div>
        </div>

  <div class="form-group row" id="post-html-btn-row">
    <label class="col-sm-2 col-form-label" for="writeup-author-slug">Post HTML:</label>
    <button type="button" class="btn btn-warning col-sm-2 offset-sm-8">Edit HTML</button>
  </div>


  <div class="form-group row" id="post-html-row">
    <label class="col-sm-2 col-form-label" for="post-html">Post HTML:</label>
            <div class="col-sm-10">
    <textarea class="form-control" id="post-html" rows="10" name="post_html">${wpv.html | n}</textarea>
            </div>
  </div>
  <div class="form-group row">
    <button type="submit" class="btn btn-success col-sm-2">Save</button>
    <button type="submit" formaction="${request.route_path('delete_extracted_post', post_id=wpv.id)}" class="btn btn-outline-danger col-sm-2 offset-sm-8">Delete</button>
  </div>

    </form>


    </div>
    <div class="card-body">
        <div class="p-3 border">
    ${wpv.html_markup}
        </div>
    </div>
</div>
<%block name="in_footer">
<script>
$(() => {
    const writeupOptionsUrl = "${request.route_path('writeup_post_options', writeup_id='replaceme')}";
    function showEl(el) {
        el.removeClass("d-none");
    }
    function hideEl(el) {
        el.addClass("d-none");
    }
    function disableEl(el) {
        el.prop("disabled", true);
    }
    function enableEl(el) {
        el.prop("disabled", false);
    }
    function row(el) {
        return el.parents(".row").first();
    }
    function writeupChange(evt) {
        const currentWriteup = $('#writeup').val();
        if (currentWriteup === 'w') {
            disableEl($('#writeup-post'))
            hideEl($('#writeup-post-row'));

            enableEl($('#writeup-title'));
            showEl(row($('#writeup-title')));
            enableEl($('#writeup-author'));
            showEl(row($('#writeup-author')));
            enableEl($('#post-title'));
            showEl(row($('#post-title')));

            return;
        }
        const skipLoad = !evt;
        disableEl($('#writeup-title'));
        hideEl(row($('#writeup-title')));
        disableEl($('#writeup-author'));
        hideEl(row($('#writeup-author')));
        disableEl($('#post-title'));
        hideEl(row($('#post-title')));

        if (skipLoad) {
            enableEl($('#writeup-post'));
            showEl($('#writeup-post-row'));
            postChange();
            return;
        }
        const fetching = fetch(writeupOptionsUrl.replace("replaceme", currentWriteup), {credentials: 'include'});
        fetching.then(resp => resp.text()).then(
            newOptions => {
                $('#writeup-post').html(newOptions);
                enableEl($('#writeup-post'));
                showEl($('#writeup-post-row'));
                postChange();
            }
        );
    }
    function postChange() {
        const currentWriteupPost = $('#writeup-post').val();
        if (currentWriteupPost === 'wp') {
            enableEl($('#post-title'));
            showEl(row($('#post-title')));
            return;
        }
        disableEl($('#post-title'));
        hideEl(row($('#post-title')));
    }
    $('#writeup').on('change', writeupChange);
    $('#writeup-post').on('change', postChange);
    writeupChange();

    $('#post-html-btn-row button').on('click', () => {
        $('#post-html-btn-row').remove()
        showEl($('#post-html-row'));
        enableEl($('#post-html-row textarea'));
    });
    hideEl($('#post-html-row'));
    disableEl($('#post-html-row textarea'));
});
</script>
</%block>