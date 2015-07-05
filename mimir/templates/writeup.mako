<%inherit file="base.mako"/>
<%block name="title">${parent.title()} &mdash; ${writeup.title}</%block>
<div class="page-header">
  <h1>${writeup.title} <small>by ${writeup.posts[0].author}</small></h1>
</div>

<div class="row post-toc">
  <div class="col-md-8">
    <table class="table table-condensed">
      <tbody>
% for post in writeup.posts:
        <tr>
          <td>${post.ordinal}</td>
          <td><a href="#${post.ordinal}">${post.title}</a></td>
        </tr>
% endfor
      </tbody>
    </table>
  </div>
</div>

% for post in writeup.posts:
% if not loop.first:
<hr>
% endif
<div id="${post.ordinal}">
<p>
  <h3>${post.title}</h3>
    <span class="author">posted by ${post.author}</span> <a href="${post.url}">Original SA post</a>
</p>
</div>
% endfor
