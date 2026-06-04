# Notes on week4_2

## 05-implementation

### Phase 1

#### The two handler functions

* The file `telegram/handlers.py` is a sea of red, because the types of so many things are `<some type> | None` that then are used as though they're never None.
I think most of these are best fixed with

```
if not <variable>:
    return
```

but you may, in later phases, plan to handle them with exceptions.
A warning to the implementer would be sporting. :-)

* My persist_with_category() from week3 has `category` instead of `category_name`
I'll go look at the notes for week3 to see what it says.
Okay, I got it wrong! Who knows why, but in both the code and the test.
I obviously know more now than I did then.

... um. No. This is a mess.  If I call the field `category` in the week4_2 code, it works, and all my tests run and pass, but it looks like there are places I find `category` fields and others where I see `category_name` fields.  Trying to fix this all up now could lead into a rat's nest of errors.

I'll stall and look at that problem later.

#### Wire it and run

Either you mean't "type  **/start**" instead of "tap **Start**" or you forgot to stick in a button.

### Phase3 Harden into a tested Conversation Handler

#### The class

`handlers.py` remains a sea of red

#### `bot.py`

This is now redder, and there is no call to the new `cancel` callback.
