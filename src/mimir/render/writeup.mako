<%inherit file="layout.mako"/>
<%block name="title">${parent.title()} &mdash; ${writeup.title}</%block>

<div class="page-header">
  <h1>${writeup.title} <small>by ${writeup.author}</small></h1>
</div>
% if writeup.offensive_content:
<img class="contentwarning" src="${request.route_path('rendered_static_file', filename='gross.png')}" alt="This RPG is pretty gross.">
% endif
% if writeup.triggery_content:
<img class="contentwarning" src="${request.route_path('rendered_static_file', filename='triggery.png')}" alt="This RPG may trigger some people.">
% endif

<div class="row post-toc">
  <div class="col-md-8">
    <table class="table table-condensed">
      <tbody>
% for post in writeup.published_posts:
        <tr>
          <td>${post.ordinal}</td>
          <td><a href="#${post.ordinal}">${post.title}</a></td>
        </tr>
% endfor
      </tbody>
    </table>
  </div>
</div>

% for post in writeup.published_posts:
% if not loop.first:
<hr>
% endif
<div id="${post.ordinal}">
<p>
  <h3>${post.title}</h3>
    <span class="author">posted by ${post.author}</span> <a href="${post.active_version.url}">Original SA post</a>
</p>
${post.active_version.html_with_fixed_image_urls(request) | n}
</div>
% endfor
<%block name="in_footer">
<script src="${request.route_path('rendered_static_file', filename='timg.js')}"></script>
</%block>