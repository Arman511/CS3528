"""This module contains the error routes for the application."""

from flask import json, redirect, render_template, session

from werkzeug import exceptions


def get_user_type():
    """Get the user type from the session data."""
    user = session.get("user")
    employer = session.get("employer")
    student = session.get("student")
    superuser = session.get("superuser")

    user_type = None
    # Determine user_type based on session data
    if superuser:
        user_type = "superuser"
    elif user:
        user_type = "admin"
    elif employer:
        user_type = "employer"
    elif student:
        user_type = "student"
    return user_type


def add_error_routes(app):
    """Register error routes for the application."""

    @app.route("/400")
    def error_400():
        """The 400 route which renders the '400.html' template.

        Returns:
            str: Rendered 400.html template.
        """
        code = 400
        name = "Bad Request"
        msg = "The server could not understand the request due to invalid syntax."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            400,
        )

    @app.route("/401")
    def error_401():
        """The 401 route which renders the '401.html' template.

        Returns:
            str: Rendered 401.html template.
        """
        code = 401
        name = "Unauthorized"
        msg = "The server could not verify that you are authorized to access the URL requested."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            401,
        )

    @app.route("/403")
    def error_403():
        """The 403 route which renders the '403.html' template.

        Returns:
            str: Rendered 403.html template.
        """
        code = 403
        name = "Forbidden"
        msg = "You don't have permission to access the requested resource."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            403,
        )

    @app.route("/404")
    def error_404():
        """The 404 route which renders the '404.html' template.

        Returns:
            str: Rendered 404.html template.
        """
        code = 404
        name = "Not Found"
        msg = "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            404,
        )

    @app.route("/405")
    def error_405():
        """The 405 route which renders the '405.html' template.

        Returns:
            str: Rendered 405.html template.
        """
        code = 405
        name = "Method Not Allowed"
        msg = "The method is not allowed for the requested URL."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            405,
        )

    @app.route("/406")
    def error_406():
        """The 406 route which renders the '406.html' template.

        Returns:
            str: Rendered 406.html template.
        """
        code = 406
        name = "Not Acceptable"
        msg = "The server can only generate a response that is not accepted by the client."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            406,
        )

    @app.route("/408")
    def error_408():
        """The 408 route which renders the '408.html' template.

        Returns:
            str: Rendered 408.html template.
        """
        code = 408
        name = "Request Timeout"
        msg = "The server timed out waiting for the request."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            408,
        )

    @app.route("/409")
    def error_409():
        code = 409
        name = "Conflict"
        msg = "The request could not be completed due to a conflict with the current state of the resource."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            409,
        )

    @app.route("/410")
    def error_410():
        code = 410
        name = "Gone"
        msg = "The requested resource is no longer available and has been permanently removed."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            410,
        )

    @app.route("/411")
    def error_411():
        code = 411
        name = "Length Required"
        msg = (
            "The server refuses to accept the request without a defined Content-Length."
        )
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            411,
        )

    @app.route("/412")
    def error_412():
        code = 412
        name = "Precondition Failed"
        msg = "The server does not meet one of the preconditions specified in the request."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            412,
        )

    @app.route("/413")
    def error_413():
        code = 413
        name = "Request Entity Too Large"
        msg = "The request is larger than the server is willing or able to process."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            413,
        )

    @app.route("/414")
    def error_414():
        code = 414
        name = "Request URI Too Large"
        msg = "The URI requested by the client is longer than the server is willing to interpret."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            414,
        )

    @app.route("/415")
    def error_415():
        code = 415
        name = "Unsupported Media Type"
        msg = "The server does not support the media type transmitted in the request."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            415,
        )

    @app.route("/416")
    def error_416():
        code = 416
        name = "Requested Range Not Satisfiable"
        msg = "The client has asked for a portion of the file that the server cannot supply."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            416,
        )

    @app.route("/417")
    def error_417():
        code = 417
        name = "Expectation Failed"
        msg = "The server cannot meet the requirements of the Expect request-header field."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            417,
        )

    @app.route("/418")
    def error_418():
        code = 418
        name = "I'm a teapot"
        msg = "The server is a teapot; it cannot brew coffee."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            418,
        )

    @app.route("/421")
    def error_421():
        code = 421
        name = "Misdirected Request"
        msg = "The request was directed at a server that is not able to produce a response."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            421,
        )

    @app.route("/422")
    def error_422():
        code = 422
        name = "Unprocessable Entity"
        msg = "The server understands the content type of the request entity, but was unable to process the contained instructions."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            422,
        )

    @app.route("/423")
    def error_423():
        code = 423
        name = "Locked"
        msg = "The resource that is being accessed is locked."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            423,
        )

    @app.route("/424")
    def error_424():
        code = 424
        name = "Failed Dependency"
        msg = "The method could not be performed on the resource because the requested action depended on another action and that action failed."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            424,
        )

    @app.route("/428")
    def error_428():
        code = 428
        name = "Precondition Required"
        msg = "The server requires the request to be conditional."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            428,
        )

    @app.route("/429")
    def error_429():
        code = 429
        name = "Too Many Requests"
        msg = "The user has sent too many requests in a given amount of time."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            429,
        )

    @app.route("/431")
    def error_431():
        code = 431
        name = "Request Header Fields Too Large"
        msg = "The server is unwilling to process the request because its header fields are too large."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            431,
        )

    @app.route("/451")
    def error_451():
        code = 451
        name = "Unavailable For Legal Reasons"
        msg = "The server is denying access to the resource as a consequence of a legal demand."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            451,
        )

    @app.route("/500")
    def error_500():
        """The 500 route which renders the '500.html' template.

        Returns:
            str: Rendered 500.html template.
        """
        code = 500
        name = "Internal Server Error"
        msg = "The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            500,
        )

    @app.route("/501")
    def error_501():
        code = 501
        name = "Not Implemented"
        msg = "The server either does not recognize the request method, or it lacks the ability to fulfill the request."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            501,
        )

    @app.route("/502")
    def error_502():
        code = 502
        name = "Bad Gateway"
        msg = "The server was acting as a gateway or proxy and received an invalid response from the upstream server."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            502,
        )

    @app.route("/503")
    def error_503():
        code = 503
        name = "Service Unavailable"
        msg = "The server is currently unavailable (because it is overloaded or down for maintenance). Generally, this is a temporary state."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            503,
        )

    @app.route("/504")
    def error_504():
        code = 504
        name = "Gateway Timeout"
        msg = "The server was acting as a gateway or proxy and did not receive a timely response from the upstream server."
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            504,
        )

    @app.route("/505")
    def error_505():
        code = 505
        name = "HTTP Version Not Supported"
        msg = (
            "The server does not support the HTTP protocol version used in the request."
        )
        return (
            render_template(
                "error_page.html",
                user_type=get_user_type(),
                code=code,
                name=name,
                msg=msg,
            ),
            505,
        )

    @app.errorhandler(exceptions.BadRequest)
    def handle_bad_request(_e):
        """Handle bad requests and render the 400 error page."""
        return redirect("/400")

    @app.errorhandler(exceptions.Unauthorized)
    def handle_unauthorized(_e):
        """Handle unauthorized errors and render the 401 error page."""
        return redirect("/401")

    @app.errorhandler(exceptions.Forbidden)
    def handle_forbidden(_e):
        """Handle forbidden errors and render the 403 error page."""
        return redirect("/403")

    @app.errorhandler(exceptions.NotFound)
    def handle_not_found(_e):
        """Handle not found errors and render the 404 error page."""
        return redirect("/404")

    @app.errorhandler(exceptions.MethodNotAllowed)
    def handle_method_not_allowed(_e):
        """Handle method not allowed errors and render the 405 error page."""
        return redirect("/405")

    @app.errorhandler(exceptions.NotAcceptable)
    def handle_not_acceptable(_e):
        """Handle not acceptable errors and render the 406 error page."""
        return redirect("/406")

    @app.errorhandler(exceptions.RequestTimeout)
    def handle_request_timeout(_e):
        """Handle request timeout errors and render the 408 error page."""
        return redirect("/408")

    @app.errorhandler(exceptions.Conflict)
    def handle_conflict(_e):
        """Handle conflict errors and render the 409 error page."""
        return redirect("/409")

    @app.errorhandler(exceptions.Gone)
    def handle_gone(_e):
        """Handle gone errors and render the 410 error page."""
        return redirect("/410")

    @app.errorhandler(exceptions.LengthRequired)
    def handle_length_required(_e):
        """Handle length required errors and render the 411 error page."""
        return redirect("/411")

    @app.errorhandler(exceptions.PreconditionFailed)
    def handle_precondition_failed(_e):
        """Handle precondition failed errors and render the 412 error page."""
        return redirect("/412")

    @app.errorhandler(exceptions.RequestEntityTooLarge)
    def handle_request_entity_too_large(_e):
        """Handle request entity too large errors and render the 413 error page."""
        return redirect("/413")

    @app.errorhandler(exceptions.RequestURITooLarge)
    def handle_request_uri_too_large(_e):
        """Handle request URI too large errors and render the 414 error page."""
        return redirect("/414")

    @app.errorhandler(exceptions.UnsupportedMediaType)
    def handle_unsupported_media_type(_e):
        """Handle unsupported media type errors and render the 415 error page."""
        return redirect("/415")

    @app.errorhandler(exceptions.RequestedRangeNotSatisfiable)
    def handle_requested_range_not_satisfiable(_e):
        """Handle requested range not satisfiable errors and render the 416 error page."""
        return redirect("/416")

    @app.errorhandler(exceptions.ExpectationFailed)
    def handle_expectation_failed(_e):
        """Handle expectation failed errors and render the 417 error page."""
        return redirect("/417")

    @app.errorhandler(exceptions.ImATeapot)
    def handle_im_a_teapot(_e):
        """Handle I'm a teapot errors and render the 418 error page."""
        return redirect("/418")

    @app.errorhandler(exceptions.MisdirectedRequest)
    def handle_misdirected_request(_e):
        """Handle misdirected request errors and render the 421 error page."""
        return redirect("/421")

    @app.errorhandler(exceptions.UnprocessableEntity)
    def handle_unprocessable_entity(_e):
        """Handle unprocessable entity errors and render the 422 error page."""
        return redirect("/422")

    @app.errorhandler(exceptions.Locked)
    def handle_locked(_e):
        """Handle locked errors and render the 423 error page."""
        return redirect("/423")

    @app.errorhandler(exceptions.FailedDependency)
    def handle_failed_dependency(_e):
        """Handle failed dependency errors and render the 424 error page."""
        return redirect("/424")

    @app.errorhandler(exceptions.PreconditionRequired)
    def handle_precondition_required(_e):
        """Handle precondition required errors and render the 428 error page."""
        return redirect("/428")

    @app.errorhandler(exceptions.TooManyRequests)
    def handle_too_many_requests(_e):
        """Handle too many requests errors and render the 429 error page."""
        return redirect("/429")

    @app.errorhandler(exceptions.RequestHeaderFieldsTooLarge)
    def handle_request_header_fields_too_large(_e):
        """Handle request header fields too large errors and render the 431 error page."""
        return redirect("/431")

    @app.errorhandler(exceptions.UnavailableForLegalReasons)
    def handle_unavailable_for_legal_reasons(_e):
        """Handle unavailable for legal reasons errors and render the 451 error page."""
        return redirect("/451")

    @app.errorhandler(exceptions.InternalServerError)
    def handle_internal_server_error(_e):
        """Handle internal server errors and render the 500 error page."""
        return redirect("/500")

    @app.errorhandler(exceptions.NotImplemented)
    def handle_not_implemented(_e):
        """Handle not implemented errors and render the 501 error page."""
        return redirect("/501")

    @app.errorhandler(exceptions.BadGateway)
    def handle_bad_gateway(_e):
        """Handle bad gateway errors and render the 502 error page."""
        return redirect("/502")

    @app.errorhandler(exceptions.ServiceUnavailable)
    def handle_service_unavailable(_e):
        """Handle service unavailable errors and render the 503 error page."""
        return redirect("/503")

    @app.errorhandler(exceptions.GatewayTimeout)
    def handle_gateway_timeout(_e):
        """Handle gateway timeout errors and render the 504 error page."""
        return redirect("/504")

    @app.errorhandler(exceptions.HTTPVersionNotSupported)
    def handle_http_version_not_supported(_e):
        """Handle HTTP version not supported errors and render the 505 error page."""
        return redirect("/505")

    @app.errorhandler(exceptions.HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = json.dumps(
            {
                "code": e.code,
                "name": e.name,
                "description": e.description,
            }
        )
        response.content_type = "application/json"
        return response
