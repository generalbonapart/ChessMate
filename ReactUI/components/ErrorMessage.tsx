import { Text } from '@radix-ui/themes'
import React, { PropsWithChildren } from 'react'

const ErrorMessage = ({children}: PropsWithChildren) => {
  if (!children) return null;

    return (
    <Text className="mb-2" color="red" as="p">{children}</Text>
  )
}

export  {ErrorMessage}