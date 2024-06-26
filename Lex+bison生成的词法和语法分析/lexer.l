%{
/* Definitions section where required C code and header files are included */
#include "parser.tab.h" 
int yywrap() { return 1; }
%}

%%

"DRAW"                  { return DRAW; }
"MOVE"                  { return MOVE; }
"COLOR"                 { return COLOR; }
"ARC"                   { return ARC; }
"RED"                   { return RED; }
"GREEN"                 { return GREEN; }
"BLUE"                  { return BLUE; }
"YELLOW"                { return YELLOW; }
"BLACK"                 { return BLACK; }
[0-9]+                  { yylval = atoi(yytext); return NUMBER; }
","                     { return COMMA; }
"("                     { return LPAREN; }
")"                     { return RPAREN; }

[ \t\n]+                { /* Ignore whitespace */ }
.                       { printf("Unexpected character: %c\n", *yytext); }

%%
