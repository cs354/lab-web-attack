from flask import Flask, session, redirect, url_for, request, render_template, g


def create_app():
    app = Flask(__name__)
    app.secret_key = b'https://n8ta.com'
    return app