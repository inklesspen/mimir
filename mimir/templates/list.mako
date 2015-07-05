<%inherit file="base.mako"/>
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
