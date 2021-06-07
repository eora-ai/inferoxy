# How to contribute

## Issues

If you want to create an issue you can use the GitHub issues tab. There are several templates for issues:
- Bug report 
- Feature request
- Blank template for other cases

## Making changes

We are working using [git-flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) approach. 
In short:
1. Create a topic branch from the base branch:
    * If you want to implement a new feature, you should take the "develop" branch
    * If you want to fix a bag, you should take the "master" branch

2. Make commits of logical and atomic units.
3. Check your changes `git diff --check` before committing.
4. Please write good commit messages in the format:
```
#11 Capitalized, short (50 chars or less) summary

More detailed explanatory text, if necessary.  Wrap it to about 72
characters or so.  In some contexts, the first line is treated as the
subject of an email and the rest of the text as the body.  The blank
line separating the summary from the body is critical (unless you omit
the body entirely); tools like rebase can get confused if you run the
two together.

Write your commit message in the imperative: "Fix bug" and not "Fixed bug"
or "Fixes bug."  This convention matches up with commit messages generated
by commands like git merge and git revert.

Further paragraphs come after blank lines.

- Bullet points are okay, too

- Typically, a hyphen or asterisk is used for the bullet, followed by a
  single space, with blank lines in between, but conventions vary here

- Use a hanging indent

If you use an issue tracker, add a reference(s) to them at the bottom,
like so:

```
5. Make sure you have added the necessary tests for your changes 
    * we won't merge your pull request if code coverage less than 80%
    * details about tests in the following section.
7. Make a pull request.

## Testing

We use [pytest](https://docs.pytest.org/en/6.2.x/) as a library for testing. Tests for each module are running separately. For example:
```bash
pytest batch_manager
```
Usually, changes have to be in one module of the Inferoxy. Therefore, before pushing, you can run tests for one module, not for all Inferoxy. Nevertheless, CI on pull requests will run all tests.
