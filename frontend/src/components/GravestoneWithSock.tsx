import React, { useState } from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { Image } from 'expo-image';

interface GravestoneWithSockProps {
  sockImageUri: string;
  style?: ViewStyle;
  gravestoneStyle?: ViewStyle;
  sockStyle?: ViewStyle;
}

export default function GravestoneWithSock({
  sockImageUri,
  style,
  gravestoneStyle,
  sockStyle,
}: GravestoneWithSockProps) {
  const [sockLoaded, setSockLoaded] = useState(false);

  return (
    <View style={[styles.gravestoneContainer, style]}>
      <Image
        source={require('../../assets/empty-gravestone.png')}
        style={[styles.gravestoneImage, gravestoneStyle, !sockLoaded && styles.hidden]}
        contentFit="contain"
        cachePolicy="memory-disk"
      />
      <Image
        source={{ uri: sockImageUri }}
        style={[styles.sockOnGravestone, sockStyle, !sockLoaded && styles.hidden]}
        contentFit="contain"
        cachePolicy="memory-disk"
        transition={200}
        onLoad={() => setSockLoaded(true)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  gravestoneContainer: {
    width: '100%',
    maxWidth: 400,
    aspectRatio: 1,
    alignSelf: 'center',
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
  },
  gravestoneImage: {
    width: '100%',
    height: '100%',
    position: 'absolute',
  },
  sockOnGravestone: {
    width: '50%',
    height: '50%',
    marginTop: '0%',
  },
  hidden: {
    opacity: 0,
  },
});
