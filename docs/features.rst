Features
========

Only unread messages from Inbox
-------------------------------

*New in version 4.2.*

You may restrict the Inbox view to only unread messages by providing the ``unread`` option
in the query string of the link.

Example::

    <a href="{% url 'postman:inbox' %}?unread">Unread messages</a>

Limit the number of retrieved messages
--------------------------------------

*New in version 4.2.*

You may ceil the number of objects retrieved from folders by providing the ``limit`` option
in the query string of the link.

Example::

    <a href="{% url 'postman:inbox' %}?limit=10">Last messages</a>

Direct write to
---------------

In the pages of your site, you can put links containing the recipient name(s).

Example::

    <a href="{% url 'postman:write' username %}">write to {{ username }}</a>

Separate multiple usernames with a ``:`` character.

Example::

    <a href="{% url 'postman:write' 'adm1:adm2:adm3' %}">write to admins</a>

Prefilled fields
----------------

You may prefill the contents of some fields by providing a query string in the link.

Example::

    <a href="{% url 'postman:write' %}?subject=details request&body=give me details about ...">
    ask for details
    </a>

Recipients Min/Max 
------------------

If you need to constraint the maximum number of recipients in the forms,
you can pass the optional ``max`` parameter to the view.
There is no parameter for a minimum number, but you can code a custom form
and pass a ``min`` parameter to the recipient field (see Advanced Usage below for details).

Views supporting the parameter are: ``WriteView``, ``ReplyView``.

But this parameter does not apply to the default ``AnonymousWriteForm`` for visitors:
The maximum is enforced to 1 (see Advanced Usage below for knowing how),
in order to keep the features available to anonymous users to a strict minimum.

Example::

    urlpatterns = [
        # ...
        re_path(r'… ✂ …', WriteView.as_view(max=3), name='write'),
        # ...
    ]

Advanced usage
~~~~~~~~~~~~~~
If you define your own custom form, you may specify a ``min`` parameter and a ``max`` parameter
to the recipients field.

For example::

    from postman.forms import WriteForm
    class MyWriteForm(WriteForm):
        recipients = CommaSeparatedUserField(label="Recipients", min=2, max=5)

If you do not want the fixed ``max`` parameter of the recipients field in your custom form,
to be superseded by the parameter passed to the view, set the ``can_overwrite_limits`` 
form attribute to ``False``.

For example::

    class MyThreeAnonymousWriteForm(MyBaseAnonymousWriteForm):
        can_overwrite_limits = False
        recipients = CommaSeparatedUserField(label="Recipients", max=3)

See also:

* the ``POSTMAN_DISALLOW_MULTIRECIPIENTS`` setting in :ref:`optional_settings`

User filter
-----------

If there are some situations where a user should not be a recipient, you can write a filter
and pass it to the view.

Views supporting a user filter are: ``WriteView``, ``ReplyView``.

Example::

    def my_user_filter(user):
        if user.get_profile().is_absent:
            return "is away"
        return None

    urlpatterns = [
        # ...
        re_path(r'… ✂ …',
            WriteView.as_view(user_filter=my_user_filter), name='write'),
        # ...
    ]

The filter will be called for each recipient, for validation.

*Input*:

* ``user``: a User instance, as the recipient of the message

*Output*:

If the recipient is allowed, just return ``None``.

To forbid the message, use one of these means:

* return ``False`` or ``''``, if you do not want to give a reason for the refusal.
  The error message will be: "Some usernames are rejected: foo, bar."

* return a string, as a reason for the refusal.
  The error message will be: "Some usernames are rejected: foo (reason), bar (reason)."

* raise a ``ValidationError`` with an error message to your liking.

Advanced usage
~~~~~~~~~~~~~~

If you define your own custom form, you may specify a user filter inside.

For example::

    def my_user_filter(user):
        # ...
        return None

    from postman.forms import WriteForm
    class MyWriteForm(WriteForm):
        recipients = CommaSeparatedUserField(label="Recipients", user_filter=my_user_filter)

Exchange filter
---------------

If there are some situations where an exchange should not take place, you can write a filter
and pass it to the view.
Typical usages would be: blacklists, users that do not want solicitation from visitors.

Views supporting an exchange filter are: ``WriteView``, ``ReplyView``.

An example, with the django-relationships application::

    def my_exchange_filter(sender, recipient, recipients_list):
        if recipient.relationships.exists(sender, RelationshipStatus.objects.blocking()):
            return "has blacklisted you"
        return None

    urlpatterns = [
        # ...
        re_path(r'… ✂ …',
            WriteView.as_view(exchange_filter=my_exchange_filter),
            name='write'),
        # ...
    ]

The filter will be called for each couple, to validate that the exchange is possible.

(*New in version 3.3.0*)
In the case of a reply, there is an additional call for the implicit recipient when it is a User.
The value of the ``recipients_list`` parameter allows to differentiate the context.

*Inputs*:

* ``sender``: a User instance, as the sender of the message, or None if the writer is not authenticated
* ``recipient``: a User instance, as the recipient of the message
* ``recipients_list``: the full list of recipients
  or (*New in version 3.3.0*) None in the case of the implicit recipient for a reply.
  Provided as a convenient additional element of decision.

*Output*:

If the exchange is allowed, just return ``None``.

To forbid the exchange, use one of these means:

* return ``False`` or ``''``, if you do not want to give a reason for the refusal.
  The error message will be: "Writing to some users is not possible: foo, bar."

* return a string, as a reason for the refusal.
  The error message will be: "Writing to some users is not possible: foo (reason), bar (reason)."

* raise a ``ValidationError`` with an error message to your liking.

Advanced usage
~~~~~~~~~~~~~~

If you define your own custom form, you may specify an exchange filter inside.

For example::

    def my_exchange_filter(sender, recipient, recipients_list):
        # ...
        return None

    from postman.forms import WriteForm
    class MyWriteForm(WriteForm):
        exchange_filter = staticmethod(my_exchange_filter)

Auto-complete field
-------------------

An auto-complete functionality may be useful on the recipients field.

To activate the option, set at least the ``arg_default`` key in the
``POSTMAN_AUTOCOMPLETER_APP`` dictionary.  If the default ``ajax_select`` application is used,
define a matching entry in the ``AJAX_LOOKUP_CHANNELS`` dictionary.

Example::

    AJAX_LOOKUP_CHANNELS = {
        'postman_users': dict(model='auth.user', search_field='username'),
    }
    POSTMAN_AUTOCOMPLETER_APP = {
        'arg_default': 'postman_users',
    }

Don't forget that not-custom channels are restricted to users having the ``is_staff`` property.

In case of version 1.1.4/5 of django-ajax-selects:

	Support for multiple recipients is not turned on by default by `django-ajax-selects`_.
	To allow this capability, you have to pass the option ``multiple: true`` to jquery-plugin-autocomplete.

.. _`django-ajax-selects`: https://github.com/crucialfelix/django-ajax-selects

	Make your own templates, based on these two files, given as implementation examples:

	* :file:`postman/templates/autocomplete_postman_multiple_as1-1.html`
	* :file:`postman/templates/autocomplete_postman_single_as1-1.html`

	These examples include a correction necessary for the support of the 'multiple' option.

In case of version 1.2.x of django-ajax-selects:

	Refer to the installation guide of this application, in particular the use of AJAX_SELECT_BOOTSTRAP
	and AJAX_SELECT_INLINES.
	Support for multiple recipients is not as simple as an option: see the examples in the `jQuery UI demos`_.

.. _`jQuery UI demos`: http://jqueryui.com/resources/demos/autocomplete/multiple-remote.html

	You can use the following working implementation example:

	* :file:`postman/templates/autocomplete_postman_multiple_as1-2.html`

(*New in version 3.3.0*) In case of version 1.3.x of django-ajax-selects:

	To make your own :file:`templates/autocomplete.html` or :file:`templates/autocomplete_<channel>.html`,
	you can use the following working implementation example:

	* :file:`postman/templates/autocomplete_postman_multiple_as1-3.html`

Customization
~~~~~~~~~~~~~

You may attach a specific channel, different from the default one, to a particular view.

Views supporting an auto-complete parameter are: ``WriteView``, ``ReplyView``.

For the ``WriteView`` view, the parameter is named ``autocomplete_channels`` (note the plural).
It supports two variations:

* a 2-tuple of channels names: the first one for authenticated users, the second for visitors.
  Specify ``None`` if you let the default channel name for one of the tuple parts.
* a single channel name: the same for users and visitors

For the ``ReplyView`` view, the parameter is named ``autocomplete_channel`` (note the singular).
The value is the channel name.

Example::

    urlpatterns = [
        # ...
        re_path(r'… ✂ …',
            WriteView.as_view(autocomplete_channels=(None,'anonymous_ac')),
            name='write'),
        re_path(r'… ✂ …',
            ReplyView.as_view(autocomplete_channel='reply_ac'),
            name='reply'),
        # ...
    ]

Example::

    urlpatterns = [
        # ...
        re_path(r'… ✂ …',
            WriteView.as_view(autocomplete_channels='write_ac'),
            name='write'),
        # ...
    ]

Advanced usage
~~~~~~~~~~~~~~

If you define your own custom form, you may specify an autocomplete channel inside.

For example::

    from postman.forms import WriteForm
    class MyWriteForm(WriteForm):
        recipients = CommaSeparatedUserField(label="Recipients", channel='my_channel')
