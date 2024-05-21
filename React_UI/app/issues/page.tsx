'use client'
import React, { useState } from 'react'
import {Box, Button, Table, TextField, Callout} from '@radix-ui/themes'
import { useForm } from 'react-hook-form';
import axios from 'axios';


interface InputParameters{
  clock_limit : string;        // # Time limit for each player in seconds
  clock_increment: string;     // # Time increment per move in seconds
  color: string;       //  # Choose color randomly (can also be "white" or "black")
  variant: string;    //  # Chess variant (standard, chess960, etc.)
  level : string;
}
const IssuesPage = () => {
  const {register,handleSubmit} = useForm<InputParameters>();
  const [calloutOpen, setCalloutOpen] = useState(false);
  const [calloutMessage, setCalloutMessage] = useState('');
  return (
    <>
      <form onSubmit={handleSubmit( async (data)=> 
        {
          const parameters = JSON.stringify(data,null,2);
          
          try {
            console.log(parameters)
            const response = await axios.post('/runscript', parameters, {
              headers: {
                // Overwrite Axios's automatically set Content-Type
                'Content-Type': 'application/json'
              }
            }
          );   
          setCalloutMessage('Challenge sent successfully!');
          setCalloutOpen(true);
        } catch (error) {
            console.log('Error posting input parameters: ', error);
            setCalloutMessage('Error sending challenge.');
            setCalloutOpen(true);
        }
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


              {/* Remove the predeifned values here
                parameters with uppercase doesn't work
                clock_limit must be a multiple of 60
                
              */}


            <TextField.Root size="1" placeholder="White/Black" defaultValue= "white" {...register('color')} />
            </Box>
            </Table.Cell>

            <Table.Cell>
            <Box maxWidth="150px">
              <TextField.Root size="1" placeholder="1-10" defaultValue= "4" {...register('level')}/>
            </Box>
            </Table.Cell>
            <Table.Cell>
            <Box maxWidth="150px">
              <TextField.Root size="1" placeholder="Standard, 360" defaultValue= "standard" {...register('variant')} />
            </Box>
            </Table.Cell>
            <Table.Cell>
            <Box maxWidth="150px">
              <TextField.Root size="1" placeholder="Minutes" defaultValue= "180" {...register('clock_limit')} />
            </Box>
            </Table.Cell>
            <Table.Cell>
            <Box maxWidth="150px">
              <TextField.Root size="1" placeholder="Seconds" defaultValue= "5" {...register('clock_increment')}/>
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

      {calloutOpen && (
        <Callout.Root>
          <Callout.Icon>
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.49991 0.877045C3.84222 0.877045 0.877075 3.84219 0.877075 7.49988C0.877075 11.1575 3.84222 14.1227 7.49991 14.1227C11.1576 14.1227 14.1227 11.1575 14.1227 7.49988C14.1227 3.84219 11.1576 0.877045 7.49991 0.877045ZM1.82708 7.49988C1.82708 4.36686 4.36689 1.82704 7.49991 1.82704C10.6329 1.82704 13.1727 4.36686 13.1727 7.49988C13.1727 10.6329 10.6329 13.1727 7.49991 13.1727C4.36689 13.1727 1.82708 10.6329 1.82708 7.49988ZM10.1589 5.53774C10.3178 5.31191 10.2636 5.00001 10.0378 4.84109C9.81194 4.68217 9.50004 4.73642 9.34112 4.96225L6.51977 8.97154L5.35681 7.78706C5.16334 7.59002 4.84677 7.58711 4.64973 7.78058C4.45268 7.97404 4.44978 8.29061 4.64325 8.48765L6.22658 10.1003C6.33054 10.2062 6.47617 10.2604 6.62407 10.2483C6.77197 10.2363 6.90686 10.1591 6.99226 10.0377L10.1589 5.53774Z" fill="currentColor" fill-rule="evenodd" clip-rule="evenodd"></path></svg>
          </Callout.Icon>
          <Callout.Text>{calloutMessage}</Callout.Text>
        </Callout.Root>
      )}

    </>

  )
}

export default IssuesPage