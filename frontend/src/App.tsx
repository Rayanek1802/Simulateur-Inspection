import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { ChakraProvider, Box, Container, Flex, Heading, VStack } from '@chakra-ui/react';

// Components (to be created)
import SessionForm from './components/SessionForm';
import SessionView from './components/SessionView';
import SessionList from './components/SessionList';

function App() {
  return (
    <ChakraProvider>
      <Router>
        <Box minH="100vh" bg="gray.50">
          <Box bg="blue.600" color="white" py={4} mb={8}>
            <Container maxW="container.xl">
              <Flex justify="space-between" align="center">
                <Heading size="lg">Simulateur Inspection</Heading>
                <Flex gap={4}>
                  <Link to="/">Sessions List</Link>
                  <Link to="/new">New Session</Link>
                </Flex>
              </Flex>
            </Container>
          </Box>

          <Container maxW="container.xl">
            <VStack spacing={8} align="stretch">
              <Routes>
                <Route path="/" element={<SessionList />} />
                <Route path="/new" element={<SessionForm />} />
                <Route path="/session/:id" element={<SessionView />} />
              </Routes>
            </VStack>
          </Container>
        </Box>
      </Router>
    </ChakraProvider>
  );
}

export default App; 