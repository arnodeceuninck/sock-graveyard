import React, { useState } from 'react';
import { View, StyleSheet, ViewStyle, ImageStyle } from 'react-native';
import { Image } from 'react-native';

interface GravestoneWithSockProps {
  sockImageUri: string;
  style?: ViewStyle;
  gravestoneStyle?: ImageStyle;
  sockStyle?: ImageStyle;
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
        resizeMode="contain"
      />
      <View style={styles.sockClipArea}>
        <Image
          source={{ uri: sockImageUri }}
          style={[styles.sockOnGravestone, sockStyle, !sockLoaded && styles.hidden]}
          resizeMode="contain"
          onLoad={() => setSockLoaded(true)}
        />
      </View>
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
  sockClipArea: {
    width: '30%',
    height: '50%',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
    // backgroundColor: 'rgba(255, 0, 0, 0.3)',
  },
  sockOnGravestone: {
    width: '100%',
    height: '100%',
  },
  hidden: {
    opacity: 0,
  },
});
