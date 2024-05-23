import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(req: NextRequest) {
  if (req.method === 'POST') {
    const inputParameters = await req.json();
    console.log(inputParameters)
    // Path to the Python script
    const scriptPath = path.join(process.cwd(), 'send_challenge.py')

    spawn('python', [scriptPath, JSON.stringify(inputParameters)])
    return NextResponse.json({ error: 'Post Successful' }, { status: 200 })

  } else {
    return NextResponse.json({ error: 'Method Not Allowed' }, { status: 405 })
  }
}