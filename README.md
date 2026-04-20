![Coverage](./coverage.svg)
# AAI-template
A template for my new repos in JuanJo's Agentic AI course.

- Customize ```LICENSE``` to contain my name and the year
- Make a more meaningful ```README.md``` (this file), but ***LEAVE THE FIRST (Coverage) line as-is***!
- Edit a few files to change every string that contains *AAI* to whatever my project is called.

    **N.B.** The easy way to do that is with `tools/fix-project`

    if I want a project called `expenses`, from the top-level, I only need to run this:

    ```tools/fix-project expenses```

Note: the project assumes that I launch my file with ```main.main```: that is, by executing the file ```src/<projec>/main.py```, and calling the function ```main()```.
If I want to call my primary executable something else, I'll need to find and tweak every instance of ```main```, too.
