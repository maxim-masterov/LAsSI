#include <iostream> 
#include <mpi.h>
#include <utmpx.h>
#include <string.h>
using namespace std;

void parallelinit( int** localA, int* localb, int* localc, int size, int localsize )
{
  int id;
  MPI_Comm_rank(MPI_COMM_WORLD, &id);
  for ( int i = 0; i < localsize; ++i )
  {
    for ( int j = 0; j < size; ++j )
    {
        localA[i][j] = j+localsize*id+i;
    }
  } 
  for ( int i = 0; i < size; ++i )
  {
        localb[i] = 1;
  } 
}

void init( int** A, int* b, int* c, int size )
{
  for ( int i = 0; i < size; ++i )
  {
    for ( int j = 0; j < size; ++j )
    {
        A[i][j] = j+i;
    }
  } 
  for ( int i = 0; i < size; ++i )
  {
        b[i] = 1;
  } 
}

void parallelmatvec( int** A, int* b, int* c, int size, int localsize )
{
    for ( int i = 0; i < localsize; ++i )
    {
        c[i] = 0;
    } 
    for ( int i = 0; i < localsize; ++i )
    {
        for ( int j = 0; j < size; ++j )
        {
            c[i] += A[i][j]*b[j];
        }
    }
}

void matvec( int** A, int* b, int* c, int size )
{
    for ( int i = 0; i < size; ++i )
    {
        c[i] = 0;
    } 
    for ( int i = 0; i < size; ++i )
    {
        for ( int j = 0; j < size; ++j )
        {
            c[i] += A[i][j]*b[j];
        }
    }
}

int main(int argc, char ** argv) {
  double t1, t2;
  int nproc, id;
  // init MPI
  MPI_Init(&argc, &argv);
  MPI_Comm_size(MPI_COMM_WORLD, &nproc); // get totalnodes
  MPI_Comm_rank(MPI_COMM_WORLD, &id);
  // int n = 30720;
  int n = 4*15360;
  int* c = new int[n];
  // compute
  int nlocal = n/nproc;
  int** localA = new int*[nlocal];
  for ( int i = 0; i < nlocal; ++i )
  {
    localA[i] = new int[n];
  } 
  int* localb = new int[n];
  int* localc = new int[nlocal];
  if ( nlocal*nproc != n )
  {
    std::cerr << "ERROR: totalsize of the matrix " << n << " is not a multiple of the number of processes !" << std::endl;
    //    exit(0);
  }
  int* displs = new int[nproc];
  int* recvcnts = new int[nproc];
  displs[0] = 0;
  recvcnts[0]=nlocal;
  for ( int i=1; i<nproc; ++i )
  {
    displs[i] = displs[i-1]+nlocal;
    recvcnts[i]=nlocal;
  }
  if (id == 0) 
  {
    t1 = MPI_Wtime();
  }

  // int itest = 0;
  // int itest2 = 0;
  // for (int i = 0; i<nlocal*1000; ++i)
  //   {
  //     itest=itest+1;
  //     for (int j =0; j<1000; ++j)
  // 	{
  // 	  itest2 = itest%7;
  // 	}
  //   }
  // std::cout << itest << itest2 << std::endl;

  parallelinit(localA, localb, localc, n, nlocal);
  parallelmatvec(localA, localb, localc, n, nlocal);
  MPI_Gatherv( localc, nlocal, MPI_INT, c, recvcnts, displs, MPI_INT, 0, MPI_COMM_WORLD);
  
  MPI_Barrier(MPI_COMM_WORLD);
  //
  if (id == 0) 
  {
    t2 = MPI_Wtime();
    // check result
    int** globalA = new int*[n];
    for ( int i = 0; i < n; ++i )
    {
      globalA[i] = new int[n];
    }
    int* globalb = new int[n];
    int* globalc = new int[n];
    init(globalA, globalb, globalc, n);
    matvec(globalA, globalb, globalc, n);
    bool result_ok = true;
    for ( int i = 0; i < n; ++i )   
    {
      if (c[i] != globalc[i])
      {
	std::cout << "at index " << i << " -- " << c[i] << " != " << globalc[i] << std::endl;
	result_ok = false;
	break;
      }
    }
    if ( result_ok )
    {
      std::cout << "result OK" << endl;
    }
    else
    {
      std::cout << "ERROR: result is wrong in parallel" << endl;
    }

    std::cout << "time elapsed: " << (t2 - t1) << endl;

    delete[] globalb;
    delete[] globalc;
    for ( int i = 0; i < n; ++i )
    {
      delete[] globalA[i];
    } 
    delete[] globalA;

  }
  //
  MPI_Barrier(MPI_COMM_WORLD);
  // check processes scheduling
  char processor_name[MPI_MAX_PROCESSOR_NAME];
  int processor_name_len;
  MPI_Get_processor_name(processor_name, &processor_name_len);
  int total_len = 0;
  //get hostname of each process on root proc
  int* recvcounts_hostname = new int[nproc];
  int* displs_hostname = new int[nproc];
  MPI_Gather(&processor_name_len, 1, MPI_INT, recvcounts_hostname, 1, MPI_INT, 0, MPI_COMM_WORLD);
  if ( id==0 )
  {
    displs_hostname[0]=0;
    for ( int i = 1; i < nproc; ++i )
    {
      displs_hostname[i]=displs_hostname[i-1] + recvcounts_hostname[i-1];
    }
    total_len = displs_hostname[nproc-1]+recvcounts_hostname[nproc-1];
  }
  char* processor_name_arrays = new char[total_len];
  MPI_Gatherv( processor_name, processor_name_len, MPI_CHAR, processor_name_arrays, recvcounts_hostname, displs_hostname, MPI_CHAR, 0, MPI_COMM_WORLD );
  int* sched_cpu_array = new int[nproc];
  int cpunb = sched_getcpu();
  MPI_Gather(&cpunb, 1, MPI_INT, sched_cpu_array, 1, MPI_INT, 0, MPI_COMM_WORLD);
  //
  MPI_Barrier(MPI_COMM_WORLD);
  if ( id == 0 )  // master process
  {
    bool scheduling_ok = true;
    for ( int i=0; i<nproc; ++i )
    {
      for ( int j=0; j<nproc; ++j )
      {
	//check if processes i and j are on the same hostname
	bool same_node = true;
	if( i == j )
	{
	  same_node=true;
	}
	else if(recvcounts_hostname[i] == recvcounts_hostname[j])
	{
	  for (int k = 0; k < recvcounts_hostname[i]; ++k)
	  {
	    if(processor_name_arrays[displs_hostname[i]+k] != processor_name_arrays[displs_hostname[j]+k])
	    {
	      same_node = false;
	    }
	  }
	}
	else
	{
	  same_node = false;
	}
	
	// check if processes i and j are on a different cpu
	if( same_node && (i != j) && (sched_cpu_array[i] == sched_cpu_array[j]) )
	{
	  std::cout << "ERROR: ";
	  for ( int k = 0; k < recvcounts_hostname[i]; ++k )
          {
	    std::cout << processor_name_arrays[displs_hostname[i]+k];
          }
	  std::cout << " sched_cpu_array[" << i << "] = " << sched_cpu_array[i] << "  ==  " << "sched_cpu_array[" << j << "] = " <<sched_cpu_array[j] << std::endl;
	  scheduling_ok = false;
	}
      }
    }
    if ( scheduling_ok )
    {
      std::cout << "scheduling OK" << std::endl;
    }
    else
    {
      std::cout << "ERROR: scheduling of the MPI processes is wrong - at least 2 processes are running on the same CPU" << endl;      
    }
  }  
  MPI_Barrier(MPI_COMM_WORLD);
  //  std::cout << "Hello from P" << id << " / " << nproc << " - hostname " << processor_name << " - cpu = " << cpunb << std::endl;
  //
  // delete vars
                                                                                        
  delete[] recvcounts_hostname;
  delete[] displs_hostname;
  delete[] processor_name_arrays;
  delete[] sched_cpu_array;
  delete[] recvcnts;
  delete[] displs;
  delete[] localb;
  delete[] localc;
  for ( int i = 0; i < nlocal; ++i )
  {
    delete[] localA[i];
  } 
  delete[] localA;
  // delete global var
  delete[] c;
  MPI_Finalize();

  return 0;
}



