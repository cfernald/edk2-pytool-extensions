# Pytool Extensions Environment Variables

EDK2 Pytool Extensions have a few enviornment variables that can be set to alter how the
utilities behave (mostly Stuart). To clarify, these are not variables that target how a
project might CI or build, but they alter how the tools themselves behave when executing
these functions.

The general philosophy around when an environment variable is made available is: the output
of the utility or process should be exactly the same whether the variable is provided or not,
and regardless of the contents of the variable. They are only to be used to optimize or
otherwise make working with the utilities more ergonomic. If this axiom does not hold true,
it's likely that the setting should be a command line argument.

## OMNICACHE_PATH

This variable, if present, will enable the Stuart tools that clone or update Git repositories
to use the local Omnicache rather than having to fetch everything from the server. This can
greatly improve the performance of CI processes that have to clone many dependencies.

For more info, see [the Omnicache docs](using_omnicache.md).

## STUART_EXTDEP_CACHE_PATH

This is similar to the Omnicache, but for binary dependencies and tools. If present, will
enable Stuart to both populate and query the local cache for dependencies like Nuget and
Web dependencies. After the initial fetch, this can greatly improve the performance of
calling `stuart_update` and make it far easier to switch between multiple branches or
scopes where dependencies may change.

For more info, see [the External Dependencies docs](using_extdep.md).
