<%inherit file="layout.mako"/>
<%block name="in_header">
<style type="text/css">
blockquote {
  padding: 10.5px 21px;
  margin: 0 0 21px;
  border-left: 5px solid #ecf0f1;
}
</style>
</%block>
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="${request.route_path('index')}">Home</a></li>
    <li class="breadcrumb-item active" aria-current="page">Thread #${thread_page.thread_id}</li>
  </ol>
</nav>

<hr>
<div>
<form class="form-inline" action="${request.route_path('refetch_page', thread_id=thread_page.thread.id, page_num=thread_page.page_num)}" method="POST">
  <button type="submit" class="btn btn-primary mb-2">Refetch</button>
  <label class="ml-2">Last fetched: ${thread_page.last_fetched | n,nicedt}</label>
</form>
</div>

<%block name="pagination_els">
<nav aria-label="Thread navigation">
  <ul class="pagination">
    <li class="page-item${"" if pagination['enable_prev'] else " disabled"}">
    % if pagination['enable_prev']:
      <a class="page-link" href="${request.route_path('thread_page', thread_id=thread_page.thread.id, page_num=thread_page.page_num-1)}" aria-label="Previous">
        <span aria-hidden="true">&laquo;</span>
      </a>
    % else:
        <span class="page-link" aria-label="Previous">&laquo;</span>
    % endif
    </li>
    % for page_num in pagination['pages']:
    % if page_num == thread_page.page_num:
    <li class="page-item active" aria-current="page"><span class="page-link">${page_num}</span></li>
    % else:
    <li class="page-item"><a class="page-link" href="${request.route_path('thread_page', thread_id=thread_page.thread.id, page_num=page_num)}">${page_num}</a></li>
    % endif
    % endfor
    <li class="page-item${"" if pagination['enable_next'] else " disabled"}">
    % if pagination['enable_prev']:
      <a class="page-link" href="${request.route_path('thread_page', thread_id=thread_page.thread.id, page_num=thread_page.page_num+1)}" aria-label="Next">
        <span aria-hidden="true">&raquo;</span>
      </a>
    % else:
        <span class="page-link" aria-label="Next">&raquo;</span>
    % endif
    </li>
  </ul>
</nav>
</%block>

% for thread_post in thread_page.posts:
<div class="card" id="post-${thread_post.id}">
    <div class="card-header">
        <ul class="list-inline mb-0">
            <li class="list-inline-item"><a href="${thread_post.url}">#${thread_post.id}</a></li>
            <li class="list-inline-item">${thread_post.author}</li>
            <li class="list-inline-item">Extracted: ${"☑︎" if thread_post.has_been_extracted else "□"}</li>
            <li class="list-inline-item">In Writeup: ${"☑︎" if thread_post.is_in_writeup else "□"}</li>
            <li class="list-inline-item float-right">
              <form class="form-inline" action="${request.route_path('extract_post', post_id=thread_post.id)}" method="POST">
                <button type="submit" class="btn btn-outline-primary btn-sm">Extract</button>
              </form>
            </li>
        </ul>
    </div>
    <div class="card-body">
    ${thread_post.html_markup}
    </div>
</div>
%endfor
${pagination_els()}
