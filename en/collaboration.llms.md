# 46  Version control and collaboration with Git and Github

This chapter presents an overview of using Git to collaborate with others. More extensive tutorials can be found at the bottom in the Resources section.

## 46.1 What is Git?

Git is a **version control** software that allows tracking changes in a folder. It can be used like the “track change” option in Word, LibreOffice or Google docs, but for all types of files. It is one of the most powerful and most used options for version control.

**Why have I never heard of it? -** While people with a developer background routinely learn to use version control software (Git, Mercurial, Subversion or others), few of us from quantitative disciplines are taught these skills. Consequently, most epidemiologists never hear of it during their studies, and have to learn it on the fly.

**Wait, I heard of Github, is it the same?** - Not exactly, but you often use them together, and we will show you how to. In short:

- **Git** is the version control system, a piece of software. You can use it locally on your computer or to synchronize a folder with a host **website**. By default, one uses a terminal to give Git instructions in command-line.

- You can use a **Git client/interface** to avoid the command-line and perform the same actions (at least for the simple, super common ones).

- If you want to store your folder in a **host website** to collaborate with others, you may create an account at Github, Gitlab, Bitbucket or others.

So you could use the client/interface **Github Desktop**, which uses **Git** in the background to manage your files, both locally on your computer, and remotely on a **Github** server.

## 46.2 Why use the combo Git and Github?

Using **Git** facilitates:

1.  Archiving documented versions with incremental changes so that you can easily revert backwards to any previous state
2.  Having parallel *branches*, i.e. developing/“working” versions with structured ways to integrate the changes after review

This can be done locally on your computer, even if you don’t collaborate with other people. Have you ever:

- regretted having deleted a section of code, only to realize two months later that you actually needed it?

- come back on a project that had been on pause and attempted to remember whether you had made that tricky modification in one of the models?

- had a *file model_1.R* and another file *model_1_test.R* and a file *model_1_not_working.R* to try things out?

- had a file *report.Rmd*, a file *report_full.Rmd*, a file *report_true_final.Rmd*, a file *report_final_20210304.Rmd*, a file *report_final_20210402.Rmd* and cursed your archiving skills?

Git will help with all that, and is worth to learn for that alone.

However, it becomes even more powerful when used with a online repository such as Github to support **collaborative projects**. This facilitates:

- Collaboration: others can review, comment on, and accept/decline changes

- Sharing your code, data, and outputs, and invite feedback from the public (or privately, with your team)

and avoids:

- “Oops, I forgot to send the last version and now you need to redo two days worth of work on this new file”

- Mina, Henry and Oumar all worked at the same time on one script and need to manually merge their changes

- Two people try to modify the same file on Dropbox and Sharepoint and this creates a synchronization error.

### This sounds complicated, I am not a programmer

It can be. Examples of advanced uses can be quite scary. However, much like R, or even Excel, you don’t need to become an expert to reap the benefits of the tool. Learning a *small number of functions and notions* lets you track your changes, synchronize your files on a online repository and collaborate with your colleagues in a very short amount of time.

Due to the learning curve, emergency context may not be the best of time to learn these tools. But learning can be achieved by steps. Once you acquire a couple of notions, your workflow can be quite efficient and fast. If you are not working on a project where collaborating with people through Git is a necessity, **it is actually a good time to get confident using it** in solo before diving in collaboration.

## 46.3 Setup

### Install Git

*Git* is the engine behind the scenes on your computer, which tracks changes, branches (versions), merges, and reverting. **You must first install *Git* from <https://git-scm.com/downloads>.**

### Install an interface (optional but recommended)

Git has its own language of commands, which can be typed into a command line terminal. However, there are many clients/interfaces and as non-developpers, in your day-to-day use, you will rarely *need* to interact with Git directly and interface usually provide nice visualisation tools for file modifications or branches.

Many options exist, on all OS, from beginner friendly to more complex ones. Good options for beginners include the RStudio Git pane and [Github Desktop](https://desktop.github.com/), which we will showcase in this chapter. Intermediate (more powerfull, but more complex) options include Source Tree, Gitkracken, Smart Git and others.

Quick explanation on [Git clients](https://happygitwithr.com/git-client.html#git-client).

*Note: since interfaces actually all use Git internally, you can try several of them, switch from one to another on a given project, use the console punctually for an action your interface does not support, or even perform any number of actions online on Github.*

As noted below, you may occasionally have to write Git commands into a terminal such as the RStudio terminal pane (a tab adjacent to the R Console) or the Git Bash terminal.

### Github account

Sign-up for a free account at [github.com](https://github.com).

You may be offered to set-up two-factor authentication with an app on your phone. Read more in the Github [help documents](https://docs.github.com/en/github/authenticating-to-github/securing-your-account-with-two-factor-authentication-2fa).

If you use Github Desktop, you can enter your Gitub credentials after installation following these [steps](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop/authenticating-to-github). If you don’t do it know, credentials will be asked later when you try to clone a project from Github.

## 46.4 Vocabulary, concepts and basic functions

As when learning R, there is a bit of vocabulary to remember to understand Git. Here are the [basics to get you going](https://www.freecodecamp.org/news/an-introduction-to-git-for-absolute-beginners-86fa1d32ff71/) / [interactive tutorial](https://learngitbranching.js.org). In the next sections, we will show how to use interfaces, but it is good to have the vocabulary and concepts in mind, to build your mental model, and as you’ll need them when using interfaces anyway.

### Repository

A Git *repository* (“*repo*”) is a folder that contains all the sub-folders and files for your project (data, code, images, etc.) and their revision histories. When you begin tracking changes in the repository with it, Git will create a hidden folder that contains all tracking information. A typical Git repository is your *R Project* folder (see handbook page on [R projects](r_projects.llms.md)).

We will show how to create (*initialize*) a Git repository from Github, Github Desktop or Rstudio in the next sections.

### Commits

A *commit* is a **snapshot** of the project at a given time. When you make a change to the project, you will make a new commit to track the changes (the delta) made to your files. For example, perhaps you edited some lines of code and updated a related dataset. Once your changes are saved, you can bundle these changes together into one “commit”.

Each commit has a unique ID (a *hash*). For version control purposes, you can revert your project back in time based on commits, so it is best to keep them relatively small and coherent. You will also attach a brief description of the changes called the “commit message”.

*Staged changes*? To stage changes is to add them to the *staging area* in preparation for the next commit. The idea is that you can finely decide which changes to include in a given commit. For example, if you worked on model specification in one script, and later on a figure in another script, it would make sense to have two different commits (it would be easier in case you wanted to revert the changes on the figure but not the model).

### Branches

A branch represents an *independent line* of changes in your repo, a parallel, alternate version of your project files.

Branches are useful to test changes before they are incorporated into the *main* branch, which is usually the primary/final/“live” version of your project. When you are done experimenting on a branch, you can bring the changes into your *main* branch, by *merging* it, or delete it, if the changes were not so successful.

*Note: you do not have to collaborate with other people to use branches, nor need to have a remote online repository.*

### Local and remote repositories

To *clone* is to create a copy of a Git repository in another place.

For example, you can *clone* a online repository *from* Github locally on your computer, or begin with a local repository and clone it online *to* Github.

When you have cloned a repository, the project files exist in two places:

- the *LOCAL* repository on your physical computer. This is where you make the actual changes to the files/code.

- the *REMOTE*, online repository: the versions of your project files in the Github repository (or on any other web host).

To synchronize these repositories, we will use more functions. Indeed, unlike Sharepoint, Dropbox or other synchronizing software, Git does not automatically update your local repository based or what’s online, or vice-versa. You get to choose when and how to synchronize.

- `git fetch` downloads the new changes from the remote repository but does not change your local repository. Think of it as checking the state of the remote repository.

- `git pull` downloads the new changes from the remote repositories and update your local repository.

- When you have made one or several commits locally, you can `git push` the commits to the remote repository. This sends your changes on Github so that other people can see and pull them if they want to.

## 46.5 Get started: create a new repository

There are many ways to create new repositories. You can do it from the console, from Github, from an interface.

Two general approaches to set-up are:

- Create a new R Project from an existing or new Github repository (*preferred for beginners*), or
- Create a Github repository for an existing R project

### Start-up files

When you create a new repository, you can optionally create all of the below files, or you can add them to your repository at a later stage. They would typically live in the “root” folder of the repository.

- A *README* file is a file that someone can read to understand why your project exists and what else they should know to use it. It will be empty at first, but you should complete it later.

- A *.gitignore* file is a text file where each line would contain folders or files that Git should ignore (not track changes). Read more about it and see examples [here](https://www.freecodecamp.org/news/gitignore-what-is-it-and-how-to-add-to-repo/).

- You can choose a *license* for your work, so that other people know under which conditions they can use or reproduce your work. For more information, see the [Creative Commons licenses](https://creativecommons.org/licenses/).

### Create a new repository in Github

To create a new repository, log into Github and look for the green button to create a new repository. This now empty repository can be cloned locally to your computer (see next section).

[![](../../images/github_new.png)](../../images/github_new.png)

You must choose if you want your repository to be **public** (visible to everyone on the internet) or **private** (only visible to those with permission). This has important implications if your data are sensitive. If your repository is private you will encounter some quotas in advanced special circumstances, such as if you are using Github *actions* to automatically run your code in the cloud.

### Clone from a Github repository

You can *clone* an existing Github repository to create a new local R project on your computer.

The Github repository could be one that already exists and contains content, or could be an empty repository that you just created. In this latter case you are essentially creating the Github repo and local R project at the same time (see instructions above).

*Note*: if you do not have contributing rights on a Github repository, it is possible to first *fork* the repository to your profile, and then proceed with the other actions. Forking is explained at the end of this chapter, but we recommend that you read the other sections first.

Step 1: Navigate in Github to the repository, click on the green “**Code**” button and copy the **HTTPS clone URL** (see image below)

[![](../../images/github_clone.png)](../../images/github_clone.png)

The next step can be performed in any interface. We will illustrate with Rstudio and Github desktop.

#### In Rstudio

In RStudio, start a new R project by clicking *File \> New Project \> Version Control \> Git*

- When prompted for the “Repository URL”, paste the HTTPS URL from Github  
- Assign the R project a short, informative name  
- Choose where the new R Project will be saved locally  
- Check “Open in new session” and click “Create project”

You are now in a new, local, RStudio project that is a clone of the Github repository. This local project and the Github repository are now linked.

#### In Github Desktop

- Click on *File \> Clone a repository*

- Select the URL tab

- Paste the HTTPS URL from Github in the first box

- Select the folder in which you want to have your local repository

- Click “CLONE”

[![](../../images/github_clone_desktop.png)](../../images/github_clone_desktop.png)

### New Github repo from existing R project

An alternative setup scenario is that you have an existing R project with content, and you want to create a Github repository for it.

1.  Create a new, empty Github repository for the project (see instructions above)  
2.  Clone this repository locally (see HTTPS instructions above)  
3.  Copy all the content from your pre-existing R project (codes, data, etc.) into this new empty, local, repository (e.g. use copy and paste).  
4.  Open your new project in RStudio, and go to the Git pane. The new files should register as file changes, now tracked by Git. Therefore, you can bundle these changes as a *commit* and *push* them up to Github. Once *pushed*, the repository on Github will reflect all the files.

See the Github workflow section below for details on this process.

### What does it look like now?

#### In RStudio

Once you have cloned a Github repository to a new R project, you now see in RStudio a “Git” tab. This tab appears in the same RStudio pane as your R Environment:

[![](../../images/git_console.png)](../../images/git_console.png)

Please note the buttons circled in the image above, as they will be referenced later (from left to right):

- Button to *commit* the saved file changes to the local branch (this will open a new window)
- Blue arrow to *pull* (update your local version of the branch with any changes made on the remote/Github version of that branch)
- Green arrow to *push* (send any commits/changes for your local version of the branch to the remote/Github version of that branch)
- The Git tab in RStudio
- Button to create a NEW branch using whichever local branch is shown to the right as the base. *You almost always want to branch off from the main branch (after you first pull to update the main branch)*
- The branch you are currently working in
- Changes you made to code or other files will appear below

#### In Github Desktop

Github Desktop is an independent application that allows you to manage all your repositories. When you open it, the interface allows you to choose the repository you want to work on, and then to perform basic Git actions from there.

[![](../../images/github_desktop_interface.png)](../../images/github_desktop_interface.png)

## 46.6 Git + Github workflow

### Process overview

Once you have completed the setup (described above), you will have a Github repo that is connected (*cloned*) to a local R project. The *main* branch (created by default) is the so-called “live” version of *all* the files. When you want to make modifications, it is a good practice to create a *new branch* from the *main* branch (like “Make a Copy”). This is a typical workflow in Git because creating a branch is easy and fast.

A typical workflow is as follow:

1.  Make sure that your local repository is up-to-date, update it if not

2.  Go to the branch you were working on previously, or create a new branch to try out some things

3.  Work on the files locally on your computer, make one or several commits to this branch

4.  Update the remote version of the branch with your changes (push)

5.  When you are satisfied with your branch, you can merge the online version of the working branch into the online “main” branch to transfer the changes

Other team members may be doing the same thing with their own branches, or perhaps contributing commits into your working branch as well.

We go through the above process step-by-step in more detail below. Here is a schematic we’ve developed - it’s in the format of a two-way table so it should help epidemiologists understand.

[![](../../images/github_table.png)](../../images/github_table.png)

Here’s [another diagram](https://build5nines.com/introduction-to-git-version-control-workflow/).

*Note: until recently, the term “master” branch was used, but it is now referred to as “main” branch.*

[![](../../images/github-flow.png)](../../images/github-flow.png)

Image [source](https://build5nines.com/introduction-to-git-version-control-workflow/)

## 46.7 Create a new branch

When you select a branch to work on, **Git resets your working directory the way it was the last time you were on this branch**.

### In Rstudio Git pane

Ensure you are in the “main” branch, and then click on the purple icon to create a new branch (see image above).

- You will be prompted to name your branch with a one-word descriptive name (can use underscores if needed).
- You will see that locally, you are still in the same R project, but you are no longer working on the “main” branch.
- Once created, the new branch will also appear in the Github website as a branch.

You can visualize branches in the Git Pane in Rstudio after clicking on “History”

[![](../../images/github_rstudio_branchs.png)](../../images/github_rstudio_branchs.png)

### In Github Desktop

The process is very much similar, you are prompted to give your branch a name. After, you will be prompted to “Publish you branch to Github” to make the new branch appear in the remote repo as well.

[![](../../images/github_desktop_new_branch.png)](../../images/github_desktop_new_branch.png)

### In console

What is actually happening behind the scenes is that you create a new branch with `git branch`, then go to the branch with `git checkout` (*i.e.* tell Git that your next commits will occur there). From your git repository:

``` bash
git branch my-new-branch  # Create the new branch branch
git checkout my-new-branch # Go to the branch
git checkout -b my-new-branch # Both at once (shortcut)
```

For more information about using the console, see the section on Git commands at the end.

## 46.8 Commit changes

Now you can edit code, add new files, update datasets, etc.

Every one of your changes is tracked, *once the respective file is saved*. Changed files will appear in the RStudio Git tab, in Github Desktop, or using the command `git status` in the terminal (see below).

Whenever you make substantial changes (e.g. adding or updating a section of code), pause and *commit* those changes. Think of a commit as a “batch” of changes related to a common purpose. You can always continue to revise a file after having committed changes on it.

*Advice on commits*: generally, it is better to make small commits, that can be easily reverted if a problem arises, to commit together modifications related to a common purpose. To achieve this, you will find that *you should commit often*. At the beginning, you’ll probably forget to commit often, but then the habit kicks in.

### In Rstudio

The example below shows that, since the last commit, the R Markdown script “collaboration.Rmd” has changed, and several PNG images were added.

[![](../../images/github_tracking2.png)](../../images/github_tracking2.png)

You might be wondering what the yellow, blue, green, and red squares next to the file names represent. Here is a snapshot from the [RStudio cheatsheet](https://www.rstudio.com/wp-content/uploads/2016/01/rstudio-IDE-cheatsheet.pdf) that explains their meaning. Note that changes with yellow “?” can still be staged, committed, and pushed.

[![](../../images/github_tracking.png)](../../images/github_tracking.png)

- Press the “Commit” button in the Git tab, which will open a new window (shown below)

- Click on a file name in the upper-left box

- Review the changes you made to that file (highlighted below in green or red)

- “Stage” the file, which will include those changes in the commit. Do this by checking the box next to the file name. Alternatively, you can highlight multiple file names and then click “Stage”

- Write a commit message that is short but descriptive (required)

- Press the “Commit” button. A pop-up box will appear showing success or an error message.

Now you can make more changes and more commits, as many times as you would like

[![](../../images/github_commit.png)](../../images/github_commit.png)

### In Github Desktop

You can see the list of the files that were changed on the left. If you select a text file, you will see a summary of the modifications that were made in the right pane (the view will not work on more complex files like .docs or .xlsx).

To stage the changes, just tick the little box near file names. When you have selected the files you want to add to this commit, give the commit a name, optionally a description and then click on the **commit** button.

[![](../../images/github_desktop_commit.png)](../../images/github_desktop_commit.png)

### In console

The two functions used behind the scenes are `git add` to select/stage files and `git commit` to actually do the commit.

``` bash
git status # see the changes 

git add content/en/collaboration.qmd  # select files to commit (= stage the changes)

git commit -m "Describe commit from Github Desktop" # commit the changes with a message

git log  # view information on past commits
```

### Amend a previous commit

What happens if you commit some changes, carry on working, and realize that you made changes that should “belong” to the past commit (in your opinion). Fear not! You can append these changes to your previous commit.

In Rstudio, it should be pretty obvious as there is a “Amend previous commit” box on the same line as the COMMIT button.

For some unclear reason, the functionality has not been implemented as such in Github Desktop, but there is a (conceptually awkward but easy) way around. If you have committed **but not pushed** your changes yet, an “UNDO” button appears just under the COMMIT button. Click on it and it will revert your commit (but keep your staged files and your commit message). Save your changes, add new files to the commit if necessary and commit again.

In the console:

``` bash
git add [YOUR FILES] # Stage your new changes

git commit --amend  # Amend the previous commit

git commit --amend -m "An updated commit message"  # Amend the previous commit AND update the commit message
```

*Note: think before modifying commits that are already public and shared with your collaborators*.

## 46.9 Pull and push changes up to Github

“First PULL, then PUSH”

It is good practice to *fetch* and *pull* before you begin working on your project, to update the branch version on your local computer with any changes that have been made to it in the remote/Github version.

PULL often. Don’t hesitate. *Always pull before pushing*.

When your changes are made and committed and you are happy with the state of your project, you can *push* your commits up to the remote/Github version of your branch.

Rince and repeat while you are working on the repository.

**Note:** it is much easier to revert changes that were committed but not pushed (i.e. are still local) than to revert changes that were pushed to the remote repository (and perhaps already pulled by someone else), so it is better to push when you are done with introducing changes on the task that you were working on.

#### In Rstudio

*PULL* - First, click the “Pull” icon (downward arrow) which fetches and pulls at the same time.

*PUSH* - Clicking the green “Pull” icon (upward arrow). You may be asked to enter your Github username and password. The first time you are asked, you may need to enter two Git command lines into the *Terminal*:

- **git config –global user.email “<you@example.com>”** (your Github email address), and  
- **git config –global user.name “Your Github username”**

To learn more about how to enter these commands, see the section below on Git commands.

***TIP:*** Asked to provide your password too often? See these chapters 10 & 11 of this [tutorial](https://happygitwithr.com/credential-caching.html#credential-caching) to connect to a repository using a SSH key (more complicated)

#### In Github Desktop

Click on the “Fetch origin” button to check if there are new commits on the remote repository.

[![](../../images/github_desktop_fetch_button.png)](../../images/github_desktop_fetch_button.png)

If Git finds new commits on the remote repository, the button will change into a “Pull” button. Because the same button is used to push and pull, you cannot push your changes if you don’t pull before.

[![](../../images/github_desktop_pull_button.png)](../../images/github_desktop_pull_button.png)

You can go to the “History” tab (near the “Changes” tab) to see all commits (yours and others). This is a nice way of acquainting yourself with what your collaborators did. You can read the commit message, the description if there is one, and compare the code of the two files using the *diff* pane.

[![](../../images/github_desktop_history.png)](../../images/github_desktop_history.png)

Once all remote changes have been pulled, and at least one local change has been committed, you can push by clicking on the same button.

[![](../../images/github_desktop_push_button.png)](../../images/github_desktop_push_button.png)

#### Console

Without surprise, the commands are *fetch*, *pull* and *push*.

``` bash
git fetch  # are there new commits in the remote directory?
git pull   # Bring remote commits into your local branch
git push   # Puch local commits of this branch to the remote branch
```

### I want to pull but I have local work

This can happen sometimes: you made some changes on your local repository, but the remote repository has commits that you didn’t pull.

Git will refuse to pull because it might overwrite your changes. There are several strategies to keep your changes, well described in [Happy Git with R](https://happygitwithr.com/pull-tricky.html), among which the two main ones are: - commit your changes, fetch remote changes, pull them in, resolve conflicts if needed (see section below), and push everything online - `stash` your changes, which sort of stores them aside, pull, unstash (restore), and then commit, solve any conflicts, and push.

If the files concerned by the remote changes and the files concerned by your local changes do not overlap, Git may solve conflicts automatically.

In Github Desktop, this can be done with buttons. To stash, go to *Branch \> Stash all changes*.

[![](../../images/github_desktop_stash.png)](../../images/github_desktop_stash.png)

## 46.10 Merge branch into Main

If you have finished making changes, you can begin the process of merging those changes into the main branch. Depending on your situation, this may be fast, or you may have deliberate review and approval steps involving teammates.

### Locally in Github Desktop

One can merge branches locally using Github Desktop. First, go to (checkout) the branch that will be the recipient of the commits, in other words, the branch you want to update. Then go to the menu *Branch \> Merge into current branch* and click. A box will allow you to select the branch you want to import from.

[![](../../images/github_desktop_merge.png)](../../images/github_desktop_merge.png)

### In console

First move back to the branch that will be the recipient of the changes. This is usually *master*, but it could be another branch. Then merge your working branch into master.

``` bash
git checkout master  # Go back to master (or to the branch you want to move your )
git merge this_fancy_new_branch
```

[This page](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging) shows a more advanced example of branching and explains a bit what is happening behind the scenes.

### In Github: submitting pull requests

While it is totally possible to merge two branches locally, or without informing anybody, a merge may be discussed or investigated by several people before being integrated to the master branch. To help with the process, Github offers some discussion features around the merge: the **pull request**.

A pull request (a “PR”) is a request to merge one branch into another (in other words, a request that *your working branch be pulled into the “main” branch*). A pull request typically involves multiple commits. A pull request usually begins a conversation and review process before it is accepted and the branch is merged. For example, you can read pull request discussions on [dplyr’s github](https://github.com/tidyverse/dplyr/pulls).

You can submit a pull request (PR) directly form the website (as illustrated bellow) or from Github Desktop.

- Go to Github repository (online)
- View the tab “Pull Requests” and click the “New pull request” button
- Select from the drop-down menu to merge your branch into main
- Write a detailed Pull Request comment and click “Create Pull Request”.

In the image below, the branch “forests” has been selected to be merged into “main”:

[![](../../images/github_pull_request2.png)](../../images/github_pull_request2.png)

Now you should be able to see the pull request (example image below):

- Review the tab “Files changed” to see how the “main” branch would change if the branch were merged.  
- On the right, you can request a review from members of your team by tagging their Github ID. If you like, you can set the repository settings to require one approving review in order to merge into main.  
- Once the pull request is approved, a button to “Merge pull request” will become active. Click this.  
- Once completed, delete your branch as explained below.

[![](../../images/github_pull_request.png)](../../images/github_pull_request.png)

### Resolving conflicts

When two people modified the same line(s) at the same time, a merge conflict arises. Indeed, Git refuses to make a decision about which version to keep, but it helps you find where the conflict is. **DO NOT PANIC**. Most of the time, it is pretty straightforward to resolve.

For example, on Github:

[![](../../images/github_conflict2.png)](../../images/github_conflict2.png)

After the merge raised a conflict, open the file in your favorite editor. The conflict will be indicated by series of characters:

[![](../../images/github_conflict3.png)](../../images/github_conflict3.png)

The text between *\<\<\<\<\<\<\< HEAD* and *=======* comes from your local repository, and the one between *=======* and *\>\>\>\>\>\>\>* from the the other branch (which may be origin, master or any branch of your choice).

You need to decide which version of the code you prefer (or even write a third, including changes from both sides if pertinent), delete the rest and remove all the marks that Git added *(\<\<\<\<\<\<\< HEAD, =======, \>\>\>\>\>\>\> origin/master/your_branch_name*).

Then, save the file, stage it and commit it : this is the commit that makes the merged version “official”. Do not forget to push afterwards.

The more often you and your collaborators pull and push, the smaller the conflicts will be.

*Note: If you feel at ease with the console, there are more [advanced merging options](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging) (e.g. ignoring whitespace, giving a collaborator priority etc.).*

### Delete your branch

Once a branch was merged into master and is no longer needed, you can delete it.

#### Github + Rstudio

Go to the repository on Github and click the button to view all the branches (next to the drop-down to select branches). Now find your branch and click the trash icon next to it. Read more detail on deleting a branch [here](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-and-deleting-branches-within-your-repository#deleting-a-branch).

Be sure to also delete the branch locally on your computer. This will not happen automatically.

- From RStudio, make sure you are in the Main branch
- Switch to typing Git commands in the RStudio “Terminal” (the tab adjacent to the R console), and type: **git branch -d branch_name**, where “branch_name” is the name of your branch to be deleted
- Refresh your Git tab and the branch should be gone

#### In Github Desktop

Just checkout the branch you want to delete, and go to the menu *Branch \> Delete*.

### Forking

You can fork a project if you would like to contribute to it but do not have the rights to do so, or if you just want to modify it for your personal use. A short description of forking can be found [here](https://guides.github.com/activities/forking/).

On Github, click on the “Fork” button:

[![](../../images/github_fork_1.png)](../../images/github_fork_1.png)

This will clone the original repository, but in your own profile. So now, there are two versions of the repository **on Github**: the original one, that you cannot modify, and the cloned version in your profile.

Then, you can proceed to clone your version of the online repository locally on your computer, using any of the methods described in previous sections. Then, you can create a new branch, make changes, commit and push them *to your remote repository*.

Once you are happy with the result you can create a Pull Request from Github or Github Desktop to begin the conversation with the owners/maintainers of the original repository.

**What if you need some newer commits from the official repository?**

Imagine that someone makes a critical modification to the official repository, which you want to include to your cloned version. It is possible to synchronize your fork with the official repository. It involves using the terminal, but it is not too complicated. You mostly need to remember that: - *upstream* = the official repository, the one that you could not modify - *origin* = your version of the repository on your Github profile

You can read [this tutorial](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork) or follow along below:

First, type in your Git terminal (inside your repo):

``` bash
git remote -v
```

If you have not yet configured the upstream repository you should see two lines, beginning by *origin*. They show the remote repo that `fetch` and `push` point to. Remember, *origin* is the conventional nickname for your own version of the repository on Github. For example:

[![](../../images/github_fork_2.png)](../../images/github_fork_2.png)

Now, add a new remote repository:

``` bash
git remote add upstream https://github.com/appliedepi/epirhandbook_eng.git
```

Here the address is the address that Github generates when you clone a repository (see section on cloning). Now you will have four remote pointers:

[![](../../images/github_fork_3.png)](../../images/github_fork_3.png)

Now that the setup is done, whenever you want to get the changes from the original (*upstream*) repository, you just have to go (*checkout*) to the branch you want to update and type:

``` bash
git fetch upstream # Get the new commits from the remote repository
git checkout the_branch_you_want_to_update
git merge upstream/the_branch_you_want_to_update  # Merge the upstream branch into your branch.
git push # Update your own version of the remote repo
```

If there are conflicts, you will have to solve them, as explained in the Resolving conflicts section.

**Summary**: forking is cloning, but on the Github server side. The rest of the actions are typical collaboration workflow actions (clone, push, pull, commit, merge, submit pull requests…).

*Note: while forking is a concept, not a Git command, it also exist on other Web hosts, like [Bitbucket](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow).*

[![](../../images/github_fork_4.png)](../../images/github_fork_4.png)

## 46.11 What we learned

You have learned how to:

- setup Git to track modifications in your folders,  
- connect your local repository to a remote online repository,  
- commit changes,  
- synchronize your local and remote repositories.

All this should get you going and be enough for most of your needs as epidemiologists. We usually do not have as advanced usage as developers.

However, know that should you want (or need) to go further, Git offers more power to simplify commit histories, revert one or several commits, cherry-pick commits, etc. Some of it may sound like pure wizardry, but now that you have the basics, it is easier to build on it.

Note that while the Git pane in Rstudio and Github Desktop are good for beginners / day-to-day usage in our line of work, they do not offer an interface to some of the intermediate / advanced Git functions. Some more complete interfaces allows you to do more with point-and-click (usually at the cost of a more complex layout).

Remember that since you can use any tool at any point to track your repository, you can very easily install an interface to try it out sometimes, or to perform some less common complex task occasionally, while preferring a simplified interface for the rest of time (e.g. using Github Desktop most of the time, and switching to SourceTree or Gitbash for some specific tasks).

## 46.12 Git commands

### Recommended learning

To learn Git commands in an interactive tutorial, see [this website](https://learngitbranching.js.org/).

### Where to enter commands

You enter commands in a Git shell.

*Option 1* You can open a new Terminal in RStudio. This tab is next to the R Console. If you cannot type any text in it, click on the drop-down menu below “Terminal” and select “New terminal”. Type the commands at the blinking space in front of the dollar sign “\$”.

[![](../../images/github_terminal.png)](../../images/github_terminal.png)

*Option 2* You can also open a *shell* (a terminal to enter commands) by clicking the blue “gears” icon in the Git tab (near the RStudio Environment). Select “Shell” from the drop-down menu. A new window will open where you can type the commands after the dollar sign “\$”.

*Option 3* Right click to open “Git Bash here” which will open the same sort of terminal, or open *Git Bash* form your application list. [More beginner-friendly informations on Git Bash](https://happygitwithr.com/shell.html), how to find it and some bash commands you will need.

### Sample commands

Below we present a few common git commands. When you use them, keep in mind which branch is active (checked-out), as that will change the action!

In the commands below, represents a branch name. represents the hash ID of a specific commit. represents a number. Do not type the \< or \> symbols.

| Git command | Action |
|----|----|
| `git branch <name>` | Create a new branch with the name |
| `git checkout <name>` | Switch current branch to |
| `git checkout -b <name>` | Shortcut to create new branch *and* switch to it |
| `git status` | See untracked changes |
| `git add <file>` | Stage a file |
| `git commit -m <message>` | Commit currently staged changes to current branch with message |
| `git fetch` | Fetch commits from remote repository |
| `git pull` | Pull commits from remote repository in current branch |
| `git push` | Push local commits to remote directory |
| `git switch` | An alternative to `git checkout` that is being phased in to Git |
| `git merge <name>` | Merge branch into current branch |
| `git rebase <name>` | Append commits from current branch on to branch |

## 46.13 Resources

Much of this page was informed by [this “Happy Git with R” website](https://happygitwithr.com/) by Jenny Bryan. There is a very helpful section of this website that helps you troubleshoot common Git and R-related errors.

The [Github.com documentation and start guide](https://docs.github.com/en/github).

The RStudio [“IDE” cheatsheet](https://www.rstudio.com/wp-content/uploads/2016/01/rstudio-IDE-cheatsheet.pdf) which includes tips on Git with RStudio.

<https://ohi-science.org/news/github-going-back-in-time>

**Git commands for beginners**

An [interactive tutorial](https://learngitbranching.js.org) to learn Git commands.

<https://www.freecodecamp.org/news/an-introduction-to-git-for-absolute-beginners-86fa1d32ff71/>: good for learning the absolute basics to track changes in one folder on you own computer.

Nice schematics to understand branches: <https://speakerdeck.com/alicebartlett/git-for-humans>

**Tutorials covering both basic and more advanced subjects**

<https://tutorialzine.com/2016/06/learn-git-in-30-minutes>

<https://dzone.com/articles/git-tutorial-commands-and-operations-in-git> <https://swcarpentry.github.io/git-novice/> (short course) <https://rsjakob.gitbooks.io/git/content/chapter1.html>

The [Pro Git book](https://git-scm.com/book/en/v2) is considered an official reference. While some chapters are ok, it is usually a bit *technical*. It is probably a good resource once you have used Git a bit and want to learn a bit more precisely what happens and how to go further.
