<%inherit file="layout.mako"/>
<%block name="in_header">
<style type="text/css">
caption {
    caption-side: top;
}
</style>
</%block>
<nav class="navbar navbar-light bg-light">
    <form class="form-inline mr-auto" action="${request.route_path('render_site')}" method="POST">
        <button name="render-changed" type="submit" class="btn btn-primary my-2 my-sm-0 mr-2">Render Changed</button>
        <button name="render-all" type="submit" class="btn btn-secondary my-2 my-sm-0">Render All</button>
    </form>
    <span class="navbar-text mr-4">
    % if active_cred:
    SA Username: ${active_cred.username}
    % else:
    Signed out of SA
    % endif
    </span>
    <form class="form-inline my-2 my-lg-0 mr-auto" action="${request.route_path('fetch_threads')}" method="POST">
        <button type="submit" class="btn btn-secondary my-2 my-sm-0">Fetch Threads</button>
    </form>
    <span class="navbar-text mr-4">Mimir Username: ${request.authenticated_userid}</span>
    <form class="form-inline my-2 my-lg-0" action="${request.route_path('logout')}" method="POST">
        <button type="submit" class="btn btn-danger my-2 my-sm-0">Logout</button>
    </form>
</nav>

<table class="table table-striped table-hover">
<caption>Pending Changes</caption>
<thead><tr><th>Time</th><th>Detail</th></tr></thead>
<tbody>
% for ge in changelog_entries['generic']:
<tr>
    <td>${ge.created_at | n,nicedt}</td><td>${ge.detail}</td>
</tr>
% endfor
% for we in changelog_entries['writeup']:
<tr>
    <td>${we.created_at | n,nicedt}</td><td>${we.writeup_post.writeup.title} - ${we.writeup_post.ordinal} - ${we.writeup_post.title}</td>
</tr>
% endfor
</table>

<table class="table table-striped table-hover">
<caption>Threads</caption>
<thead><tr><th>Thread</th><th>Page Count</th><th>Open/Active</th><th>Actions</th></tr></thead>
<tbody>
% for thread in threads:
<tr>
    <td><a href="${request.route_path('thread_page', thread_id=thread.id, page_num=1)}">${thread.id}</a></td>
    <td>${thread.page_count}</td>
    <td>${"□" if thread.closed else "☑︎"}</td>
    <td>
        <ul class="list-inline">
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

<div>
% for wpv in wpvs:
<div class="card" id="post-${wpv.thread_post.id}">
    <div class="card-header">
        <ul class="list-inline mb-0">
            <li class="list-inline-item"><a href="${request.route_path('extracted_post', post_id=wpv.id)}">#${wpv.thread_post.id}</a></li>
            <li class="list-inline-item">${wpv.thread_post.author}</li>
            <li class="list-inline-item">Likely Writeup: ${wpv.writeup_guess}</li>
        </ul>
    </div>
</div>
% endfor
</div>

<table class="table table-striped table-hover">
<caption>Writeups</caption>
<thead><tr><th>Writeup</th><th>Author</th><th>Status</th><th>Published</th></tr></thead>
<tbody>
% for writeup in writeups:
<tr>
    <td><a href="${request.route_path('writeup', writeup_id=writeup.id)}">${writeup.title}</a></td>
    <td>${writeup.author_slug}</td>
    <td>${writeup.status}</td>
    <td>${"☑︎" if writeup.published else "□"}</td>
</tr>
% endfor
</tbody>
</table>