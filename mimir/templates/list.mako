<%inherit file="base.mako"/>
<p>
These writeups are extracted from the SA Forum's "FATAL & Friends" thread. Some of them are obscure RPGs. Some of them are very bad RPGs.
</p>
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
            <td><a href="${request.route_url('writeup', author_slug=writeup.author_slug, writeup_slug=writeup.writeup_slug)}">${writeup.title}</a></td>
            <td>${writeup.posts[0].author}</td>
            <td>${writeup.status}</td>
          </tr>
          % endfor          
        </tbody>
      </table>
