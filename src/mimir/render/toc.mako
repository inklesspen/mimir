<%inherit file="layout.mako"/>
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

<p>
These writeups are extracted from the SA Forum's "FATAL & Friends" thread. Some of them are obscure RPGs. Some of them are very bad RPGs.
</p>
<p><a href="${request.route_path('rendered_changelist')}">Recent Changes</a> (<a href="${request.route_path('rendered_changelist_rss')}">RSS</a>, <a href="${request.route_path('rendered_changelist_atom')}">Atom</a>, or <a href="${request.route_path('rendered_changelist_json')}">JSON</a> feed)</p>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Game Reviewed</th>
            <th>Reviewer</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          % for writeup in writeups:
          <tr>
            <td><a href="${request.route_path('rendered_writeup', author_slug=writeup.author_slug, writeup_slug=writeup.writeup_slug)}">${writeup.title}</a></td>
            <td>${writeup.author}</td>
            <td>${writeup.status}</td>
          </tr>
          % endfor          
        </tbody>
      </table>
