import os
import re
#from String import letters
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Body(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class MainPage(Handler):
    def render_NewPost(self, title="", body="", error=""):
        body1 = db.GqlQuery("SELECT * FROM Body ORDER BY created DESC LIMIT 5")
        self.render("newpost.html", title=title, body=body, error=error, body1=body1)

    def get(self):
        self.render_NewPost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Body(title = title, body = body)
            a.put()
            id = a.key().id()
            self.redirect("/%s" %id)
        else:
            error = "we need both a title and body!"
            self.render_NewPost(title, body, error)

class NewPost1(Handler):
    def render_NewPost(self, title="", body="", error=""):
        body1 = db.GqlQuery("SELECT * FROM Body ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, body=body, error=error, body1=body1)
    def get(self):
        self.render_NewPost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post = Body(
                title=title,
                body=body,
                error=error)
            post.put()

            # get the id of the new post, so we can render the post's page (via the permalink)
            id = post.key().id()
            self.redirect("/%s" %id)
        else:
            error = "we need both a title and a body!"
            self.render_NewPost(title, body, error)

class ViewPostHandler(Handler):
    def get(self, id):
        post = Body.get_by_id(int(id))
        if post:
            t = jinja_env.get_template("post.html")
            response = t.render(post=post)
        else:
            error = "there is no post with id %s" % id
            t = jinja_env.get_template("404.html")
            response = t.render(error=error)
        self.response.out.write(response)

app = webapp2.WSGIApplication([
    ('/newpost', MainPage),
    ('/', NewPost1),
     webapp2.Route('/<id:\d+>', ViewPostHandler)
], debug=True)
