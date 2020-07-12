Under-the-hood Design:

    Similar to the pset8 finance problem, I am using flask to run my website along with a two python files called application.py
and helpers.py (everything in helpers is just being called by lines of code in application.py). I use the same apology as was
apart of the starter code for finance and also use the same look-up and login_required functions from finance with modifications
to fit my project.

    In application.py, I use the starter code from finance for the functions register, login and logout and well as the error
handling functions. There are some minor modificaitons in login to fit with what I needed for my project. Along with these two
python files, I have eight other templates where the html pages are actually constructed. I am able to pass in data I need from
the dining API, dates, and data from the ingredients database (using sql commands) to the html template files.

    Within the html files, they all have a similar heading as it is from the finance problem set with minor changes. I use
the {{}} and the {% %} to use the parameters passed into the html pages. Instead of using a styles.css style sheet, all style
code is inside all tags. I wasn't planning on this originally but it became more convenient as I progressed.