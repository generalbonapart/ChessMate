'use client';
import Link from 'next/link'
import React from 'react'
import { TiCode } from "react-icons/ti";
import { usePathname } from 'next/navigation';
import classNames from 'classnames';
const NavBar = () => {
    const currentPath = usePathname();
    const links = [
        {label: 'Dashboard', href:'/'},
        {label: 'Issue Challenge', href:'/issues'},
        
    ]
  return (
    <nav className='flex space-x-6 border-b mb-5 px-5 h-14 items-center'>
        <Link href="/"><TiCode /></Link>
        <ul className='flex space-x-6'>
            {links.map(link => 
            <Link key = {link.href} 
            className={classNames({
              'text-amber-500': link.href === currentPath,
              'text-zinc-500': link.href!!=currentPath,
              'hover:text-zinc-800 transition-colors':true
            })}
            href = {link.href}>{link.label}</Link> )}
        </ul>
    </nav>
  )
}

export default NavBar