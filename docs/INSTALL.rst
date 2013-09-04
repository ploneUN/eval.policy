eval.policy Installation
------------------------

To install eval.policy using zc.buildout and the plone.recipe.zope2instance
recipe to manage your project, you can do this:

* Add ``eval.policy`` to the list of eggs to install, e.g.:

    [buildout]
    ...
    eggs =
        ...
        eval.policy

* Re-run buildout, e.g. with:

    $ ./bin/buildout

