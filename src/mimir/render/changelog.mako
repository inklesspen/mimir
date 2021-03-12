<%inherit file="layout.mako"/>
<%block name="title">${parent.title()} &mdash; Recent Changes</%block>
<%block name="in_header">
<style type="text/css">
.table {
  width: 100%;
  max-width: 100%;
  margin-bottom: 21px;
}
.table > thead > tr > th,
.table > tbody > tr > td {
  padding: 8px;
  line-height: 1.42857143;
  vertical-align: top;
}
.table > thead > tr > th {
  vertical-align: bottom;
}

.table-hover > tbody > tr:hover > td {
  background-color: #f7e8df;
}
</style>
</%block>

<div class="page-header">
  <h1>Recent Changes</h1>
</div>

      <table class="table table-hover">
        ## <thead>
        ##   <tr>
        ##     <th>Game Reviewed</th>
        ##     <th>Reviewer</th>
        ##     <th>Status</th>
        ##   </tr>
        ## </thead>
        <tbody>
          % for batch in batches:
          <tr>
          <td>
          <p id="${batch.id.base62}">${batch.created_at | n,nicedt}</p>
          % for generic_entry in batch.generic_entries:
          <p>${generic_entry.detail}</p>
          % endfor
          <ul>
          % for writeup_entry in batch.writeup_entries:
          <li><a href="${request.route_path('rendered_writeup', author_slug=writeup_entry.writeup_post.writeup.author_slug, writeup_slug=writeup_entry.writeup_post.writeup.writeup_slug)}">${writeup_entry.writeup_post.writeup.title}</a> - Post ${writeup_entry.writeup_post.ordinal} - ${writeup_entry.writeup_post.title}</li>
          % endfor
          </ul>
          </td>
            ## <td><a href="${request.route_path('rendered_writeup', author_slug=writeup.author_slug, writeup_slug=writeup.writeup_slug)}">${writeup.title}</a></td>
            ## <td>${writeup.author}</td>
            ## <td>${writeup.status}</td>
          </tr>
          % endfor          
        </tbody>
      </table>

<%def name="batch_feed_html(batch)">
% for generic_entry in batch.generic_entries:
<p>${generic_entry.detail}</p>
% endfor
<ul>
% for writeup_entry in batch.writeup_entries:
<li><a href="${request.route_url('rendered_writeup', author_slug=writeup_entry.writeup_post.writeup.author_slug, writeup_slug=writeup_entry.writeup_post.writeup.writeup_slug)}">${writeup_entry.writeup_post.writeup.title}</a> - Post ${writeup_entry.writeup_post.ordinal} - ${writeup_entry.writeup_post.title}</li>
% endfor
</ul>
</%def>