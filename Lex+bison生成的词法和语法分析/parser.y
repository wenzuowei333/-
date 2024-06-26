%{
#include <stdio.h>
#include <stdlib.h>
/* Definitions section where required C code and header files are included */
extern int yylex();
extern int yyerror(char *s);

%}

%token DRAW MOVE COLOR ARC RED GREEN BLUE YELLOW BLACK NUMBER COMMA LPAREN RPAREN

%start program

%%

program
    : statement_list
    ;

statement_list
    : statement
    | statement statement_list
    ;

statement
    : draw_statement
    | move_statement
    | color_statement
    | arc_statement
    ;

draw_statement
    : DRAW point point
      {
        printf("Draw from %s to %s\n", $2, $3);
      }
    ;

move_statement
    : MOVE point
      {
        printf("Move to %s\n", $2);
      }
    ;

color_statement
    : COLOR color
      {
        printf("Change color to %s\n", $2);
      }
    ;

arc_statement
    : ARC LPAREN NUMBER NUMBER NUMBER NUMBER NUMBER RPAREN
      {
        printf("Draw arc at %s with radius %d, start angle %d, end angle %d\n", $2, $3, $4, $5);
      }
    ;

point
    : LPAREN NUMBER COMMA NUMBER RPAREN
      {
        $$ = malloc(32); // ensure it's sufficient to hold the string
        sprintf($$, "(%d,%d)", $2, $4); // correctly format the string
      }
    ;

color
    : RED    { $$ = "Red"; }
    | GREEN  { $$ = "Green"; }
    | BLUE   { $$ = "Blue"; }
    | YELLOW { $$ = "Yellow"; }
    | BLACK  { $$ = "Black"; }
    ;

%%

int main() {
    printf("Enter your commands:\n");
    return yyparse();
}

int yyerror(char *s) {
    fprintf(stderr, "Error: %s\n", s);
    return 1;
}

