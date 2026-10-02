#include "ferrlog.h"
#include <cstdlib>
#include <iostream>


void ferrlog::open(char *filename)
{
#ifdef DEBUG_OBJ
  std::clog << "Objet: re�u demande d'ouverture de "<<filename<<std::endl ;
#endif

  // La destruction du fichier pr�c�dent n'est possible que si
  // aucun autre process ne l'utilise, l'ouverture est soumise
  // aux memes conditions et "resette" l'ancien ==> on le laisse.
    out = new ofstream(filename, ios::out) ;
    if (!out->good())
      {
        std::clog << "Pas pu ouvrir " << filename<< std::endl ;
        out = (ofstream*) NULL ;
      } 

//X   char *pcTmpName=NULL;
//X   pcTmpName=GetAllFileName(filename);
//X   if(pcTmpName) { 
//X     out = new ofstream(pcTmpName, ios::out) ;
//X     if (!out->good())
//X       {
//X         clog << "Pas pu ouvrir " << filename<< endl ;
//X         out = (ofstream*) NULL ;
//X       } 
//X     free (pcTmpName);
//X   }
    
#ifdef DEBUG_OBJ
    std::clog << "Le flux " <<  filename <<" est ouvert" << std::endl ;
#endif
  
} ;
//constructeur ferrlog

ferrlog::ferrlog(char *filename){
	open(filename);
      } 
// //  //   //    //   //  //  // //
ferrlog::~ferrlog()
{
#ifdef DEBUG_OBJ
  *out << "Destruction du flux Ferr" << std::endl ;
  std::clog << "Destruction du flux Ferr" << std::endl ;
#endif

    if (out->good()) {
      *out << "ferrlog stream close by ~ferrlog()" << std::endl ;
      *out << "\t(may be abnormal)" << std::endl ;
      out->flush() ;
      out->close() ;
    }
} ;
// destructeur ferrlog

// //  //   //    //   //  //  // //
ferrlog & ferrlog::flush (void) 
{
  std::clog.flush() ;
  if (out != NULL)
    out->flush() ;
  return *this ;
}
// flush

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << (char *msg)
{
  std::clog << msg ;
if (out != NULL)
  *out << msg ;
  return *this ;
} ;
// operateur ferrlog << char *

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << (const char *msg)
{
  if (msg != (char*) NULL) {
    if ( *msg == '\n' ) { // palliatif pour endl 
      std::clog << std::endl ;
      if (out != NULL)
          *out << std::endl ;
    } else {
      std::clog << msg ;
      if (out != NULL)
          *out << msg ;
    }
  }
  return *this ;
} ;
// operateur ferrlog << char *

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << (char msg)
{
  if ( msg == '\n' ) { // palliatif pour endl 
    std::clog << std::endl ;
    if (out != NULL)
      *out << std::endl ;
  } else {
    std::clog << msg ;
    if (out != NULL)
      *out << msg ;
  }
  return *this ;
} ;
// operateur ferrlog << const char 

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << (int msg)
{
  std::clog << msg ;
if (out != NULL)
  *out << msg ;
  return *this ;
} ;
// operateur ferrlog << int

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << ( long int msg) 
{
  std::clog << msg ;
if (out != NULL)
  *out << msg ;
  return *this ;
} ;
// operateur ferrlog << long int

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << ( unsigned int msg) 
{
  std::clog << msg ;
if (out != NULL)
  *out << msg ;
  return *this ;
} ;
// operateur ferrlog << unsigned int

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << (float msg)
{
  std::clog << msg ;
if (out != NULL)
  *out << msg ;
  return *this ;
} ;
// operateur ferrlog << float

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << (double msg)
{
  std::clog << msg ;
if (out != NULL)
  *out << msg ;
  return *this ;
} ;
// operateur ferrlog << double

// //  //   //    //   //  //  // //
ferrlog & ferrlog::operator << (void * msg)
{
  std::clog << msg ;
if (out != NULL)
  *out << msg ;
  return *this ;
} ;
// operateur ferrlog << void*

/*
ferrlog & ferrlog::operator << ( ostream & other) 
{
  clog << other ;
  if (out != NULL) {
    *out << other ;
  }
  return *this ;
  
} ;
*/

ferrlog & ferrlog::operator << ( string msg) 
{
  std::clog << msg ;
  if (out != NULL) {
    *out << msg ;
  }
  return *this ;
} ;

void ferrlog::close(void) {
    if (out->good()) {
      *out << "ferrlog stream close() called." << std::endl ;
      out->flush() ;
      out->close() ;
    }
}

// operateur ferrlog << string

// Historique !!
// operator ferrlog << ostream &
//void prog_terminate (int code) 
//{
//  Ferr << "Exit appel� avec valeur " << code << "\n" ;
//  delete (ferr) ;
//  exit (code) ;
//}
