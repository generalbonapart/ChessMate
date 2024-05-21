import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function POST(req: NextRequest, res: NextResponse) {
  console.log("Hello there !!!!")
  if (req.method === 'POST') {

    // const { clock_limit, clock_increment, color, variant, level } = req.body
    // const inputParameters = JSON.stringify({ clock_limit, clock_increment, color, variant, level })
    const inputParameters = await req.json();
    console.log(inputParameters)
    // Path to the Python script
    const scriptPath = path.join(process.cwd(), 'send_challenge.py')

    spawn('python3', [scriptPath, JSON.stringify(inputParameters)])
    return NextResponse.json({ error: 'Post Successful' }, { status: 200 })

  } else {
    return NextResponse.json({ error: 'Method Not Allowed' }, { status: 405 })
  }
}