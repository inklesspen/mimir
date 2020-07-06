<%inherit file="layout.mako"/>
<table class="table table-striped table-hover">
<thead><tr><th>Thread</th><th>Page Count</th><th>Open/Active</th><th>Actions</th></tr></thead>
<tbody>
% for thread in threads:
<tr>
    <td><a href="${request.route_path('thread_page', thread_id=thread.id, page_num=1)}">${thread.id}</a></td>
    <td>${thread.page_count}</td>
    <td>${"□" if thread.closed else "☑︎"}</td>
    <td>
        <ul class="list-inline">
            ## <li class="list-inline-item">Mark Open/Closed (TODO)</li>
            <li class="list-inline-item"><a href="${thread.url}">Visit on SA</a></li>
% if thread.id == last_extracted_post['thread_id']:
            <li class="list-inline-item"><a href="${request.route_path('thread_page', thread_id=thread.id, page_num=last_extracted_post['page_num'], _anchor='post-{}'.format(last_extracted_post['post_id']))}">Last Extracted</a></li>
% endif
        </ul>
    </td>
</tr>
% endfor
</tbody>
</table>
## TODO: some kind of add thread function

<div>
% for wpv in wpvs:
<div class="card" id="post-${wpv.thread_post.id}">
    <div class="card-header">
        <ul class="list-inline mb-0">
            <li class="list-inline-item"><a href="${request.route_path('extracted_post', post_id=wpv.id)}">#${wpv.thread_post.id}</a></li>
            <li class="list-inline-item">${wpv.thread_post.author}</li>
            <li class="list-inline-item">${wpv.edit_summary}</li>
            <li class="list-inline-item">Likely Writeup: ${wpv.writeup_guess}</li>
        </ul>
    </div>
</div>
% endfor
</div>

<table class="table table-striped table-hover">
<thead><tr><th>Writeup</th><th>Author</th><th>Status</th><th>Published</th></tr></thead>
<tbody>
% for writeup in writeups:
<tr>
    <td>${writeup.title}</td>
    <td>${writeup.author_slug}</td>
    <td>${writeup.status}</td>
    <td>${"☑︎" if writeup.published else "□"}</td>
</tr>
% endfor
</tbody>
</table>