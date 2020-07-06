<%inherit file="layout.mako"/>
<div class="card" id="post-${wpv.thread_post.id}">
    <div class="card-header">
        <ul class="list-inline mb-0">
            <li class="list-inline-item"><a href="${request.route_path('extracted_post', post_id=wpv.id)}">#${wpv.thread_post.id}</a></li>
            <li class="list-inline-item">${wpv.thread_post.author}</li>
            <li class="list-inline-item">${wpv.edit_summary}</li>
        </ul>
    </div>
    <div class="card-body">
    ${wpv.html_markup}
    </div>
</div>