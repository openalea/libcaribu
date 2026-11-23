#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdio>
#include <cstring>

#include <cstdlib>


#include <system.h>

char *GetAllFileName(char *nom) {
  char *pcTmpName=NULL;
  pcTmpName = (char*) malloc(MAX_PATH_LEN) ;
  
  if(true){
    if (pcTmpName == NULL){
      std::clog<<__FILE__<<" : "<<__LINE__<<" : Not enough memory"<<std::endl;
      exit (1);
    }
    // end of string
    pcTmpName[0]=0;
    
    // this #def is to be set for every Win32 compiler to run
#ifndef WIN32
    // TEMP est une macro dans system.h
    std::string sTmpName =TEMP ;
#else

    // On Win32, the %TEMP% variable _is_ variable.
    // I don't trust Windows functions when compiled by Bcc32, so 
    //I find out %TEMP% by myself  Ferr << __FILE__ " : "<< __LINE__ << '\n' ;
    // , assuming C:\ is allways read/write

    std::string  sTmpName;
    // on cherche TEMp dans l'environnement
    char ccCommande[MAX_PATH_LEN]= "echo %TEMP% > " ;
    
    strcpy(pcTmpName,"C:\\");
    strcat (pcTmpName,nom);
    strcat (ccCommande,pcTmpName);
    
    int iTest =0;
    iTest = system (ccCommande);
    if (iTest != 0) {
      std::cerr <<__FILE__<< ": Pas pu executer "<<ccCommande<<std::endl ;
      exit (20);
    };
    std::ifstream fin (pcTmpName, std::ios::in);
    
    // est-ce que FLUX >> string reserve la memoire ?
    fin >> sTmpName ;
    //clog <<"stmpname = "<< sTmpName ;
    // Attention : XP ne renvoie rien si une variable n'est pas d�finie
    // (style posix) HA 07 2004
    if (( sTmpName[0] == '%' ) || ( sTmpName.size() == 0 )) {
      std::istringstream isIn (".");
      isIn >>sTmpName ;
      std::clog << "No %TEMP% environmental found.\n";
      std::clog << "From now on the temp dir is going to be .\\."<<std::endl ;
    }
    fin.close();
    sprintf(ccCommande,"%s %s", RM, pcTmpName) ;
    system(ccCommande); 
    
    sTmpName.append("\\");
#endif

    sTmpName.append(nom);
    
    std::istringstream ssIn(sTmpName);
    ssIn >> pcTmpName ;
  }
  // sprintf(pcTmpName,"C:\\Windows\\Temp\\");
  return pcTmpName ;
}
