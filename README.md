# Overview

This programming assignment will exercise your skills with stream and
function programming.

You will use a variety of patterns in this assignment, with a particular
emphasis on the following patterns:

  1. Visitor Pattern
  2. Interpreter Pattern
  
Tip: Commit and push to your repository frequently so that the instructor
can see your incremental work. Particularly for people that struggle 
with the assignment, lots of commits will show the effort that you put
in and raise your score. Also, 

If you don't complete the assignment or your implementation has bugs, you
still need to turn in  your partial / broken implementation to receive
feedback. However, you should make sure that your work compiles. 

## Running the Tests

The tests for the assignment are contained in the TestQueryEngine
class. You can run this class as a pytest test in your IDE or from the 
command line using "pytest". Every time that you commit and push
to GitHub, GitHub Actions will compile and test your code. You can 
view the results on the "Actions" tab in your GitHub repository.

## Grading 

If you don't complete the assignment or your implementation has bugs, you
still need to turn in  your partial / broken implementation to receive
feedback. However, you should make sure that your work compiles. 

Grading process:
   1. If you have a working implementation that passes all tests, you 
      will receive a 100
   2. If you have a broken / incomplete implementation, your grade will
      be based on the number of tests that your code passes and the
      overall code quality.
   3. You may receive a pull request with code comments specifying
      aspects of your solution that you need to improve.
   4. If you receive comments, you will need to address the comments
      and commit the updated version within a week of receiving the
      comments.
   5. You may receive multiple rounds of comments before receiving a
      grade.
  
What to do:
   1. See the QueryEngine class for instructions.
   2. You will likely build on your prior work. If you do so,
      you must fix any tests that break.
   3. When your implementation is complete, make sure the 
      most up-to-date version is committed and pushed to 
      your assignment repository.
   4. One of the hardest parts of this assignment is going to be 
      figuring out the requirements. Pay careful attention to the
      example in the QueryEngine.main() method. It generates an
      abstract syntax tree, prints it out for you, and then shows
      what a manually crafted FindExpression for that syntax tree
      would look like. It is your job to implement a visitor that
      can construct the FindExpressions automatically from an 
      arbitrary syntax tree.
      
Warning! There may be typos, bugs, or other issues with the assignment.
If you encounter a bug, typo, etc., please post to the course discussion
forum to let the instructor know.

