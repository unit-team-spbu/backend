# Contribution Guidelines

This document describes the process of work that we use in our team. Remember that all this rules are here not by an accident and are based on years of experience of thousands of developers.

## How We Develop Project (Our SDLC)

[**Software Development Life Cycle**](https://stackify.com/what-is-sdlc/) - methodology with clearly defined processes for creating high-quality software. In detail, the SDLC methodology focuses on the following phases of software development.

We stick to Iterative software development style where each iteration consists of the following steps:

1. :thinking: Define Problem For the Next Iteration

    Before actually coding (which is fun!) we need to understand what we want to achieve by some date (deadline a.k.a. milestone). There we can do some business and technical analysis using as many conceptions as we need. Remember that there is no bad instruments, unsuitable only.

2. :bar_chart: Planning

    Now we finalize the results of the first stage with more strict bounds. We define deadline for current iteration using [GitHub Milestones](https://docs.github.com/en/github/managing-your-work-on-github/about-milestones), we create new issues (using [Issue Templates](https://docs.github.com/en/github/building-a-strong-community/configuring-issue-templates-for-your-repository)), assign them to developers and  manage them in [Project Boards](https://docs.github.com/en/github/managing-your-work-on-github/about-project-boards), mark them with [Labels](https://docs.github.com/en/github/managing-your-work-on-github/about-labels) and provide consistent description of what should be done.

3. :computer: Development

    Pick the issue you were assigned (or maybe you want to complete). Than create branch in your repository named like `issue/xxx`. Remember that we use this format for easier navigation across branches and issues as in this way we ensure that we have one branch per issue and we can easily navigate to it in browser. Also pick the right issue template.

    Now we code! But it's OK if you don't know what to do. Try to find info about the topic, ask other developers and notify them that you're stuck and don't know what to do next.

    Worth noting that sometimes it's better to start with writing Unit Tests for your code and only than implement required functionality. We also recommend following this approach, however it requires discipline, specific skills and deep understanding of business logic.

After we finish development we do all this steps again for the next iteration.