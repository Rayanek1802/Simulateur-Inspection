import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Heading,
  Input,
  useToast,
  VStack,
  IconButton,
} from '@chakra-ui/react';
import { FaTrash } from 'react-icons/fa';
import axios from 'axios';

interface Student {
  id: number;
  name: string;
}

const SessionForm: React.FC = () => {
  const [studentName, setStudentName] = useState('');
  const navigate = useNavigate();
  const toast = useToast();
  const API_URL = process.env.REACT_APP_API_URL;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentName.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter the student\'s name.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    try {
      const response = await axios.post(`${API_URL}/sessions/`, {
        students: [{ name: studentName }]
      });
      toast({
        title: 'Success',
        description: 'Session created successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate(`/session/${response.data.id}`);
    } catch (error) {
      console.error('Error creating session:', error);
      toast({
        title: 'Error',
        description: 'Error creating session',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <VStack spacing={8} align="stretch">
        <Heading size="lg">New Evaluation Session</Heading>
        <Box p={4} borderWidth="1px" borderRadius="lg" boxShadow="sm">
          <VStack spacing={4} align="stretch">
            <FormControl id="student-name">
              <FormLabel>Student Name</FormLabel>
              <Input
                placeholder="Enter student name"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
              />
            </FormControl>
          </VStack>
        </Box>
        <Button type="submit" colorScheme="blue">
          Create Session
        </Button>
      </VStack>
    </Box>
  );
};

export default SessionForm; 