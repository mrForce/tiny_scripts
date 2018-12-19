import subprocess
import shutil
import os
file_location = '/home/jforce/gitolite-admin/bin2018f/cse3100f18.{NETID}/{ASSIGNMENT}/{FILE}'

start_text = """\\documentclass{article}
\\usepackage{titlesec}
\\usepackage[utf8]{inputenc}
\\usepackage{spverbatim}
\\usepackage[english]{babel}
\\date{} 
\\titleformat*{\\section}{\\Huge\\bfseries}
\\titleformat*{\\subsection}{\\LARGE\\bfseries}
\\usepackage{minted}
\\usepackage[margin=1in]{geometry}
\\usemintedstyle{tango}

"""


with open('configs.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if len(line) > 1:
            config = eval(line)
            files = config['files']
            assignment = config['assignment']
            output_name = 'Fall18.3100.1.%s.tex' % assignment
            text = start_text + '\\title{CSE 3100, Fall 2018, ' + assignment.upper() + '}\\begin{document}\\maketitle'
            for example_name in ['good', 'average', 'poor']:        
                netid,grade,feedback_file = config[example_name]
                text += '\\newpage\n\\section{%s}\n' % example_name
                for file_name in files:
                    path = file_location.replace('{NETID}', netid).replace('{ASSIGNMENT}', assignment).replace('{FILE}', file_name)
                    if os.path.exists(path):                        
                        if '_' in file_name:
                            new_path = file_location.replace('{NETID}', netid).replace('{ASSIGNMENT}', assignment).replace('{FILE}', file_name.replace('_', '-'))
                            shutil.copy(path, new_path)
                            file_name = file_name.replace('_', '-')
                        text += '\n\\subsection{%s}\\inputminted{C}{%s}\n\n\\pagebreak\n' % (file_name, file_location.replace('{NETID}', netid).replace('{ASSIGNMENT}', assignment).replace('{FILE}', file_name))
                    else:
                        text +='\n\\subsection{%s}\n\n Question not attempted\n\\pagebreak' % file_name
                text += '\n\\subsection{feedback}\n\n \paragraph{Grade:} %d\n\n' % grade
                if feedback_file:
                    if isinstance(feedback_file, list):
                        for name, feedback_file_name in feedback_file:
                            text += '\\paragraph{Feedback for %s} \\begin{spverbatim}' % name
                            with open(file_location.replace('{NETID}', netid).replace('{ASSIGNMENT}', assignment).replace('{FILE}', feedback_file_name), 'r') as feedback_file_pointer:
                                text += feedback_file_pointer.read()
                            text += '\\end{spverbatim}\n'
                    else:
                        text += '\\paragraph{Feedback from TA} \\begin{spverbatim}'
                        with open(file_location.replace('{NETID}', netid).replace('{ASSIGNMENT}', assignment).replace('{FILE}', feedback_file), 'r') as feedback_file_pointer:
                            text += feedback_file_pointer.read()
                        text += '\\end{spverbatim}\n'
            text += '\n\\end{document}'
            with open(output_name, 'w') as g:
                g.write(text)
            subprocess.run(['pdflatex', '--shell-escape', output_name])
                

