%% LaTeX2e class for diploma theses
%% Based on wissdoc.cls by Roland Bless, 1996-2001
%% bless@telematik.informatik.uni-karlsruhe.de
%%
%% Adapted by: Timo Rohrberg, 2009
%% timo.rohrberg@student.kit.edu
%%
%% Additions by: Thorsten Haberecht, IPD - Chair Prof. B�hm, 2010
%% thorsten.haberecht@kit.edu


\NeedsTeXFormat{LaTeX2e}										% We do need LaTeX2e
\ProvidesClass{thesisclass}
\LoadClass[a4paper,11pt,titlepage]{scrbook}	% Class based on scrbook

%Alt, war kauptt: \RequirePackage{ngerman}										% New german orthography
\RequirePackage[english,ngerman]{babel}

%% -------------------------------
%% |          Packages           |
%% -------------------------------

% Fancy tables
\usepackage{diagbox}
\usepackage{colortbl}

% Include python code
\usepackage{listings}
\usepackage{xcolor}

% Wrap text around figure
\usepackage{wrapfig}

\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.92}

\lstdefinestyle{python-code-style}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2
}

						

\lstset{style=python-code-style}

\usepackage[english,ngerman]{babel}
\usepackage[utf8]{inputenc} % Input in ISO 8859-1 (Latin1)
\usepackage[T1]{fontenc}

\usepackage{ae}               % Almost european, virtual T1-Font
\usepackage[pdftex]{graphicx}
\usepackage{vmargin}          % Adjust margins in a simple way
\usepackage{fancyhdr}         % Define simple headings
\usepackage{caption}
\usepackage{subcaption}
\usepackage{url}
\usepackage[absolute,overlay]{textpos}
\usepackage{tikz}
\usepackage{amsfonts} 
\usepackage{algorithm2e}		  % Code-Listings
\RestyleAlgo{ruled}
% see http://www.ctan.org/tex-archive/macros/latex/contrib/algorithm2e/algorithm2e.pdf
% for more sophisticated algorithm listings


\usepackage[raiselinks=true,
						bookmarks=true,
						bookmarksopenlevel=1,
						bookmarksopen=true,
						bookmarksnumbered=true,
						hyperindex=true,
						plainpages=false,
						pdfpagelabels=true,
						pdfborder={0 0 0.5},
						colorlinks=false,						
						linkbordercolor={0 0.61 0.50},   
						citebordercolor={0 0.61 0.50}]{hyperref}  %{0.57 0.74 0.57}
						


%% -------------------------------
%% |   New Title Page Packages   |
%% -------------------------------
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{etoolbox}
\usepackage{pgfgantt} % Must be behind graphicx or will produce errors otherwise
\usepackage{rotating} % Same here (see above)

%% --- End of Packages ---
%% -------------------------------
%% | New Title Page Definitions  |
%% -------------------------------
% thesisclass
\definecolor{background}{RGB}{31,83,148}
\definecolor{titlecolor}{RGB}{255,255,255}

\newcommand{\authorDepartment}{Institute for Computer Science}
\newcommand{\authorChair}{Chair for Computer Science VI}
\newcommand{\authorAssociation}{Universität Würzburg}

\newcommand{\webadress}{www.uni-wuerzburg.de}

%% -------------------------------
%% |        Declarations         |
%% -------------------------------
\DeclareGraphicsExtensions{.svg}
%% --- End of Declarations ---



%% -------------------------------
%% |         New commands        |
%% -------------------------------
\newcommand{\changefont}[3]{\fontfamily{#1} \fontseries{#2} \fontshape{#3} \selectfont}
%\renewcommand*{\headfont}{\slshape}
%\newcommand{\captionfont}{}
\newcommand{\chapterheadfont}{}
\newcommand{\blankpage}{
 \clearpage{\pagestyle{empty}\cleardoublepage}
}
%% --- End of New Commands ---



%% -------------------------------
%% |      Globale Settings       |
%% -------------------------------
\setcounter{secnumdepth}{3} % Numbering also for \subsubsections
\setcounter{tocdepth}{3}    % Register \subsubsections in content directory

\setpapersize{A4}
\setmarginsrb{3cm}{1cm}{3cm}{1cm}{6mm}{7mm}{5mm}{15mm}

\parindent 0cm                     % Do not indent beginning of paragraph
\parskip1.5ex plus0.5ex minus0.5ex % Margin between paragraphs
%% --- End of global Settings ---



%% -------------------------------
%% |          Headings           |
%% -------------------------------
\pagestyle{fancy}
\renewcommand{\chaptermark}[1]{\markboth{\thechapter.\ #1}{}}
\fancyhf{}
\fancyhead[LE,RO]{{\headfont\thepage}}						% Left/right header for even/odd pages
\fancyhead[LO]{\headfont\nouppercase{\rightmark}}	% Header for left page (odd)
\fancyhead[RE]{\headfont\nouppercase{\leftmark}}	% Header for right page (even)
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\footrulewidth}{0pt}
\fancypagestyle{plain}{%
\fancyhf{}													% No Header and Footer fields
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[C]{\thepage}
}
%% --- End of Headings ---



%% -------------------------------
%% |      Style of captions      |
%% -------------------------------
\renewcommand{\chaptername}{}

\renewcommand{\section}{%
\@startsection{section}%
{1}		% Structure level
{0mm}	% Indention
{2ex plus 1ex minus 1ex}			% Pre-Margin
{0.5ex plus 0.5ex minus 0.5ex}		% Post-Margin
{\chapterheadfont\Large\bfseries}	% Style
}
\renewcommand{\subsection}{%
\@startsection{subsection}%
{2}		% Structure level
{0mm}	% Indention
{1.5ex plus 1ex minus 0.5ex}		% Pre-Margin
{0.3ex plus 0.3ex minus 0.3ex}		% Post-Margin
{\chapterheadfont\large\bfseries}	% Style
}
\renewcommand{\subsubsection}{%
\@startsection{subsubsection}%
{3}		% Structure level
{0mm}	% Indention
{1.5ex plus 1ex minus 0.5ex}			% Pre-Margin
{0.2ex plus 0.2ex minus 0.2ex}			% Post-Margin
{\chapterheadfont\normalsize\bfseries}	% Style
}
\renewcommand{\paragraph}{%
\@startsection{paragraph}%
{4}		% Structure level
{0mm}	% Indention
{1.3ex plus 1ex minus 0.3ex}			% Pre-Margin
{0.2ex plus 0.2ex minus 0.2ex}			% Post-Margin
{\chapterheadfont\normalsize\bfseries}	% Style
}
\renewcommand{\subparagraph}{%
\@startsection{subparagraph}%
{5}		% Structure level
{0mm}	% Indention
{1ex plus 1ex minus 0.2ex}				% Pre-Margin
{0.1ex plus 0.1ex minus 0.1ex}			% Post-Margin
{\chapterheadfont\normalsize\bfseries}	% Style
}
%% --- End of captions style ---



%% ---------------------------------
%% |   Style of chapter captions   |
%% ---------------------------------
\newlength{\chapnolen}
\newlength{\chapparlen}
\newsavebox{\chapno}
\renewcommand{\@makechapterhead}[1]{
  \vspace*{0.2\textheight}
  \vskip 15\p@
  {\parindent \z@ \raggedright \normalfont
    \ifnum \c@secnumdepth >\m@ne
      \if@mainmatter
        \savebox{\chapno}{\chapterheadfont\huge\bfseries \thechapter.}
        \settowidth{\chapnolen}{\usebox{\chapno}}
        \parbox[t]{\chapnolen}{\usebox{\chapno}}\nobreak\leavevmode
      \fi
    \fi
    \interlinepenalty\@MM
    \setlength{\chapparlen}{\textwidth}
    \addtolength{\chapparlen}{-1.0\chapnolen}
    \addtolength{\chapparlen}{-2ex}
    \leavevmode\nobreak
    \parbox[t]{\chapparlen}{\raggedright\chapterheadfont\huge \bfseries #1\par\nobreak}
    \vskip 40\p@
  }}

\renewcommand{\@makeschapterhead}[1]{
  \vspace*{50\p@}
  {\parindent \z@ \raggedright
    \normalfont
    \interlinepenalty\@M
    \chapterheadfont \huge \bfseries  #1\par\nobreak
    \vskip 40\p@
  }
}
%% --- End of chapter captions style ---



%% ---------------------------------
%% |  Style of content directory   |
%% ---------------------------------
\let\oldtableofcontents\tableofcontents
\renewcommand{\tableofcontents}{{\pdfbookmark{\contentsname}{\contentsname}\chapterheadfont\oldtableofcontents}}
\let\@olddottedtocline\@dottedtocline
\renewcommand{\@dottedtocline}[5]{\@olddottedtocline{#1}{#2}{#3}{#4}{\chapterheadfont #5}}
%% --- End of content directory style ---


%% ----------------------------------
%% |  Style of appendix numbering   |
%% ----------------------------------
 \renewcommand\appendix{\par 
   \setcounter{section}{0}% 
   \setcounter{subsection}{0}% 
   \setcounter{figure}{0}%
   \renewcommand\thesection{\Alph{section}}% 
   \renewcommand\thefigure{\Alph{section}.\arabic{figure}} 
   \renewcommand\thetable{\Alph{section}.\arabic{table}}}
%% --- End of appenix numbering style ---


%% **** END OF CLASS ****
