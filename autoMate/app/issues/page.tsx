'use client'
import React, { useState } from 'react'
import {Box, Button, Table, TextField} from '@radix-ui/themes'
import { useForm } from 'react-hook-form';
import axios from 'axios';
import { date } from 'zod';
import { spawnExe } from 'cross-spawn-windows-exe'


interface InputParameters{
  clock_limit : string;        // # Time limit for each player in seconds
  clock_increment: string;     // # Time increment per move in seconds
  color: string;       //  # Choose color randomly (can also be "white" or "black")
  variant: string;    //  # Chess variant (standard, chess960, etc.)
  level : string;
}
const IssuesPage = async() => {
  const {register,handleSubmit} = useForm<InputParameters>();
  return (
    <form onSubmit={handleSubmit( async (data)=> 
      {
        const parameters = JSON.stringify(data,null,2);
        console.log(parameters)
      //   try {
      //     
      //     const response = await axios.post('http://localhost:5000/runscript', data, {
      //       headers: {
      //         // Overwrite Axios's automatically set Content-Type
      //         'Content-Type': 'application/json'
      //       }
      //     });
      //     console.log(response)
          
      // } catch (error) {
      //     console.log('Error posting input parameters: ', error);
      // }
      //await spawnExe("./send_challenge.py", ["--arg1"]);
      }
    
    )}>
      <Table.Root variant= 'surface'>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>Color</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Level</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Variant</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Clock Limit</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Clock Increment</Table.ColumnHeaderCell>
            {/* <Table.ColumnHeaderCell className='hidden md:table-cell'>Status</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell className='hidden md:table-cell'>Created</Table.ColumnHeaderCell> */}
          </Table.Row>
        </Table.Header>
        <Table.Body>
            <Table.Row>
          <Table.Cell>
          <Box maxWidth="150px">


            {/* Remove the predeifned values here */}


          <TextField.Root size="1" placeholder="White/Black" value= "White" {...register('color')} />
          </Box>
          </Table.Cell>

          <Table.Cell>
          <Box maxWidth="150px">
            <TextField.Root size="1" placeholder="1-10" value= "4" {...register('level')}/>
          </Box>
          </Table.Cell>
          <Table.Cell>
          <Box maxWidth="150px">
            <TextField.Root size="1" placeholder="Standard, 360" value= "Standard" {...register('variant')} />
          </Box>
          </Table.Cell>
          <Table.Cell>
          <Box maxWidth="150px">
            <TextField.Root size="1" placeholder="Minutes" value= "10" {...register('clock_limit')} />
          </Box>
          </Table.Cell>
          <Table.Cell>
          <Box maxWidth="150px">
            <TextField.Root size="1" placeholder="Seconds" value= "5" {...register('clock_increment')}/>
          </Box>
          </Table.Cell>

            </Table.Row>
        </Table.Body>
      </Table.Root>
      <div className='m-3 '>
      <Button >
        Send Challenge!
      </Button>  
      </div>

    </form>
  )
}

export default IssuesPage